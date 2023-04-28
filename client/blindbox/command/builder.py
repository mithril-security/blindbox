import argparse
import os
import os.path as path
import subprocess
import abc
import typing as t
import pkgutil
import yaml
import sys
import re
from pydantic import BaseModel
from datetime import datetime

class ArtifactHistoryEntry(BaseModel):
    docker_tag: str
    docker_hash: str
    cce_policy: str
    created_timestamp: datetime
    source_image: str

class BlindBoxYml(BaseModel):
    platform: t.Literal['azure-sev', 'aws-nitro']
    build_artifacts: t.List[ArtifactHistoryEntry] = []

class BlindBoxBuilder(abc.ABC):
    def run_subprocess(self, command: t.List[str], *, text: bool = False, return_stdout: bool = False, cwd: t.Optional[str] = None, quiet: bool = False, assert_returncode: bool = True):
        human_readable = ' '.join(command)
        if not quiet:
            print(f"> Running `{human_readable}`...")

        capture_output=return_stdout
        res = subprocess.run(
            command,
            cwd=cwd,
            stdin=sys.stdin,
            capture_output=capture_output,
            text=text,
        )

        if assert_returncode and res.returncode != 0:
            if capture_output:
                print('stdout:')
                print(res.stdout)
                print('stderr:')
                print(res.stderr)
            raise ValueError(f"Command `{human_readable}` terminated with non-zero return code: {res.returncode}")

        if return_stdout:
            return res.stdout

    
    def make_blindbox_build_dir(self, project_folder: t.Optional[str] = None, build_dir: t.Optional[str] = None):
        if project_folder is None: project_folder = "."
        if build_dir is None:
            build_dir = path.join(project_folder, '.blindbox')
        
        if not path.exists(build_dir):
            os.makedirs(build_dir)

        return build_dir
    
    @staticmethod
    def get_project_settings(project_folder: t.Optional[str] = None) -> BlindBoxYml:
        if project_folder is None: project_folder = "."
        with open(path.join(project_folder, "blindbox.yml"), 'rb') as file:
            dict = yaml.safe_load(file)
        return BlindBoxYml(**dict)
    
    @staticmethod
    def save_project_settings(settings: BlindBoxYml, project_folder: t.Optional[str] = None):
        if project_folder is None: project_folder = "."
        with open(path.join(project_folder, "blindbox.yml"), 'wb') as file:
            yaml.safe_dump(settings.dict(), file, encoding='utf-8', )

    _tf_available = None
    def assert_tf_available(self):
        if self._tf_available is None:
            # Check if the terraform binary is installed
            res = subprocess.run(
                ["terraform", "--version"],
                capture_output=True,
                text=True,
            )

            self._tf_available = res.returncode == 0
            
        if not self._tf_available:
            raise Exception("Terraform CLI was not found in PATH. Follow the instructions at https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli.")
        

    _docker_available = None
    def assert_docker_available(self):
        if self._docker_available is None:
            # Check if the terraform binary is installed
            res = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
            )

            self._docker_available = res.returncode == 0
            
        if not self._docker_available:
            raise Exception("Docker CLI was not found in PATH. Follow the instructions at https://docs.docker.com/engine/install.")

    def export_docker_image(self, tag: str, target_file: str):
        self.assert_docker_available()
        self.run_subprocess(["docker", "save", tag, "-o", target_file])

    def build_docker_image(self, build_dir: str, tag: str, *, buildargs: dict = {}):
        self.assert_docker_available()
        args = ["docker", "build", "-t", tag]
        for k,v in buildargs.items():
            args += ["--build-arg", f"{k}={v}"]
        args.append(build_dir)

        self.run_subprocess(args)

    def docker_get_image_hash(self, image: str):
        self.assert_docker_available()

        hash = self.run_subprocess(
            ["docker", "images", "--no-trunc", "--quiet", image],
            quiet=True,
            return_stdout=True,
            text=True,
        )
        hash = hash.strip()
        return hash

    def tf_init_if_necessary(self, dir: str):
        self.assert_tf_available()

        if not path.exists(path.join(dir, ".terraform")):
            self.run_subprocess(["terraform", "init"], cwd=dir)

    
    def tf_apply(self, dir: str, vars: dict = {}):
        self.assert_tf_available()

        args = ["terraform", "apply"]
        for k,v in vars.items():
            args += ["--var", f"{k}={v}"]

        self.run_subprocess(args, cwd=dir)

    def copy_template(self, folder: str, file: str, package_path: str, executable: bool = False, replace: bool = False):
        data = pkgutil.get_data(__name__, package_path)
        file = path.join(folder, file)
        if not replace and path.exists(file):
            return
        with open(file, 'wb') as f:
            f.write(data)
        if executable:
            os.chmod(file, 0o775)

    def init_new_project(self, folder: t.Optional[str], **_kw): raise NotImplementedError()
    def build(self, **_kw): raise NotImplementedError()
    def deploy(self, **_kw): raise NotImplementedError()

class AzureSEVBuilder(BlindBoxBuilder):
    def __init__(self,
            settings: BlindBoxYml = None,
            *,
            cwd: t.Optional[str] = None,
            **_kw
        ):
        self.settings = settings
        self.cwd = cwd

    def init_new_project(self, folder: t.Optional[str], **_kw):
        if folder is None: folder = "."
        if folder is None: folder = self.cwd

        if not os.path.exists(folder):
            os.makedirs(folder)

        self.copy_template(folder, ".gitignore", "azure-sev/template.gitignore")
        self.copy_template(folder, "blindbox.yml", "azure-sev/template.yml")
        self.copy_template(folder, "blindbox.tf", "azure-sev/template.tf")
    
    def populate_whitelist(self,build_dir):
        ips=["168.63.129.16"] #DNS address
        pattern = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        with open("blindbox.yml","r") as file:
            ip_list = yaml.safe_load(file)['ip-rules']
            for ip in ip_list:
                if pattern.match(ip):
                    ips.append(ip)
                else:
                    print("IP syntax error. Exiting.")
                    exit()   

        with open(path.join(build_dir,"sev-start.sh"),"r+") as rewrite:
            lines = rewrite.readlines()
            rewrite.seek(0)
            for line in lines:
                if line.startswith("# iptables rules inserted from CLI"):
                    for x in ips:
                        line += "iptables -I DOCKER-USER -d " + x + " -i docker0 -j ACCEPT"+ "\n"
                rewrite.write(line)
        return ips

    def build(self, *, tag: str, build_dir: t.Optional[str], source_image: str, save: bool, **_kw):
        build_dir = self.make_blindbox_build_dir(self.cwd, build_dir)

        self.copy_template(build_dir, "Dockerfile", "azure-sev/Dockerfile")
        self.copy_template(build_dir, "sev-init.sh", "azure-sev/sev-init.sh", executable=True)
        self.copy_template(build_dir, "sev-start.sh", "azure-sev/sev-start.sh", executable=True)

        ips = self.populate_whitelist(build_dir)
        print(f"Whitelisted IPs are: ")
        print('\n'.join(map(str, ips)))

        self.export_docker_image(source_image, path.join(build_dir, source_image + '.tar'))
        self.build_docker_image(build_dir, tag, buildargs={"EMBED_IMAGE_TAR": source_image + '.tar'})

        image_hash = self.docker_get_image_hash(tag)
        print(f"Successfully built image with hash: {image_hash}")

        cce_policy = self.run_subprocess(
            ["az", "confcom", "acipolicygen", "--print-policy", "--image", image_hash],
            return_stdout=True, text=True
        )

        cce_policy = cce_policy.strip()

        entry = ArtifactHistoryEntry(
            cce_policy=cce_policy,
            created_timestamp=datetime.now(),
            docker_hash=image_hash,
            docker_tag=tag,
            source_image=source_image,
        )

        if save:
            already_saved = any((a.docker_hash == image_hash for a in self.settings.build_artifacts))
            if already_saved:
                print("Image hash already found in blindbox.yml file.")
            else:
                self.settings.build_artifacts.append(entry)
                BlindBoxBuilder.save_project_settings(self.settings, self.cwd)
                print(f"Saved artifact to project's blindbox.yml file.")
        else:
            print(f"Generated cce policy: {cce_policy}")
            print(f"Use the `--save` argument to save it to the project's blindbox.yml file.")


    def deploy(self, image: t.Optional[str], cce_policy: t.Optional[str], **_kw):
        folder = self.cwd
        if folder is None: folder = "."
        self.assert_tf_available()

        if cce_policy is None:
            entry = next((a for a in self.settings.build_artifacts if a.docker_hash == image or a.docker_tag == image), None)
            if entry is None:
                raise ValueError(f"Could not find the cce_policy value for image {image}. Please build it with `blindbox build` or provide it directly using the `--cce-policy` argument.")
            cce_policy = entry.cce_policy

        self.tf_init_if_necessary(folder)
        self.tf_apply(folder, {"image": image, "cce_policy": cce_policy})

class AWSNitroBuilder(BlindBoxBuilder):
    def __init__(self,
            settings: BlindBoxYml = None,
            *,
            cwd: t.Optional[str] = None,
            **_kw
        ):
        self.settings = settings
        self.cwd = cwd

    def init_new_project(self, folder: t.Optional[str], **_kw):
        if folder is None: folder = "."
        if folder is None: folder = self.cwd

        if not os.path.exists(folder):
            os.makedirs(folder)

        self.copy_template(folder, "blindbox.yml", "template/aws-nitro.yml")
        self.copy_template(folder, "blindbox.tf", "template/aws-nitro.tf")
    
    def build(self, *, build_directory: str, docker_image: str, **_kw):
        self.get_project_settings(self.cwd)

        self.build_docker_image(self.build_directory, self.docker_image)


def main():
    parser = argparse.ArgumentParser(description="Parser for the builder cli")
    parser.add_argument(
        "--cwd",
        "-C",
        help="manually specify the projet root"
    )
    subparsers = parser.add_subparsers(dest='command')

    init_command = subparsers.add_parser("init", help="initialize a blindbox project")
    init_command.add_argument(
        "--folder",
        "-f",
        default=".",
    )
    init_command.add_argument(
        "--platform",
        choices=["azure-sev", "aws-nitro"],
        required=True,
        help="the target platform. Either AWS Nitro containers, or Azure AMD-SEV ACI containers."
    )

    build_command = subparsers.add_parser('build', help="build a blindbox")
    build_command.add_argument(
        "--build-dir",
        type=str,
        help="the directory to build the docker image from. By default, it will use the project .blindbox folder",
    )
    build_command.add_argument(
        "--source-image",
        type=str,
        help="the source docker image",
        required=True,
    )
    build_command.add_argument(
        "--save",
        help="save the generated blindbox to the project's blindbox.yml file",
        action='store_true'
    )
    build_command.add_argument(
        "--tag",
        "-t",
        type=str,
        help="the tag to give the newly built docker image",
        required=True,
    )

    deploy_command = subparsers.add_parser('deploy', help="alias to `terraform apply`")
    deploy_command.add_argument(
        "image",
        type=str,
        help="the image to deploy. Build it first using `blindbox build`."
    )
    deploy_command.add_argument(
        "--cce-policy",
        type=str,
        help="the cce_policy of the image to deploy. Build it first using `blindbox build`."
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    settings: t.Optional[BlindBoxYml] = None
    if args.command == 'init':
        platform = args.platform
    else:
        settings = BlindBoxBuilder.get_project_settings(args.cwd)
        platform = settings.platform

    if platform not in ["azure-sev", "aws-nitro"]:
        raise ValueError(f"Platform {platform} does not exist.")

    if platform == "aws-nitro":
        builder = AWSNitroBuilder(settings, **args.__dict__)
    else:
        builder = AzureSEVBuilder(settings, **args.__dict__)

    if args.command == 'init':
        builder.init_new_project(**args.__dict__)
    elif args.command == 'build':
        builder.build(**args.__dict__)
    elif args.command == 'deploy':
        builder.deploy(**args.__dict__)

if __name__ == "__main__":
    main()
