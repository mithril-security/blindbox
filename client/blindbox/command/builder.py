import argparse
import os
import os.path as path
import subprocess
import abc
import typing as t
import pkgutil
import yaml
from blindbox.util import assert_dependency_available


if t.TYPE_CHECKING:
    import docker

class BlindBoxBuilder(abc.ABC):
    docker_client: "docker.DockerClient" = None
    def connect_docker_client(self, docker_addr: str) -> "docker.DockerClient":
        assert_dependency_available(["docker"])
        import docker

        self.docker_client = docker.DockerClient(base_url=docker_addr)
        return self.docker_client

    def build_docker_image(self, build_dir: str, tag: str) -> "docker.models.images.Image":
        results = self.docker_client.images.build(path=build_dir, tag=tag)
        image = results[0]
        for step in results[1]:
            if "stream" in step:
                print(step["stream"].strip())

        return image
    
    def make_blindbox_build_dir(self, project_folder: t.Optional[str] = None, build_dir: t.Optional[str] = None):
        if project_folder is None: project_folder = os.getcwd()
        if build_dir is None:
            build_dir = path.join(project_folder, '.blindbox')
        
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)

        return build_dir
    
    @staticmethod
    def get_project_settings(project_folder: t.Optional[str] = None):
        if project_folder is None: project_folder = os.getcwd()
        with open(path.join(project_folder, "blindbox.yml"), 'rb') as file:
            return yaml.safe_load(file)

    _tf_available = None
    def assert_tf_available(self):
        if self._tf_available is None:
            # Check if the terraform binary is installed
            res = subprocess.run(
                ["terraform", "--version"],
                capture_output=True,
                text=True,
            )

            self._tf_available = res.returncode != 0
            
        if not self._tf_available:
            raise Exception("Terraform CLI was not found in PATH.")
    
    def tf_apply(self, dir: str):
        self.assert_tf_available()

        try:
            # Check if the terraform directory exists
            if not os.path.exists(dir):
                raise Exception("Terraform directory does not exist")

            # Run the terraform apply command
            res = subprocess.run(
                ["terraform", "apply", "-auto-approve"],
                cwd=dir,
                capture_output=True,
                text=True,
            )

            print(res.stdout)
            print(res.stderr)

        except Exception as e:
            print(e)

    def copy_template(self, folder: str, file: str, package_path: str, executable: bool = False):
        data = pkgutil.get_data(__name__, package_path)
        file = path.join(folder, file)
        with open(file, 'wb') as f:
            f.write(data)
        if executable:
            os.chmod(file, 0o775)

    def init_new_project(self, folder: t.Optional[str], **_kw): raise NotImplementedError()
    def build(self, **_kw): raise NotImplementedError()
    def deploy(self, **_kw): raise NotImplementedError()

    def close(self):
        if self.docker_client is not None:
            self.docker_client.close()

class AzureSEVBuilder(BlindBoxBuilder):
    def __init__(self,
            settings: t.Any = None,
            *,
            cwd: t.Optional[str] = None,
            **_kw
        ):
        self.settings = settings
        self.cwd = cwd

    def init_new_project(self, folder: t.Optional[str], **_kw):
        if folder is None: folder = os.getcwd()
        if folder is None: folder = self.cwd

        if not os.path.exists(folder):
            os.makedirs(folder)

        self.copy_template(folder, ".gitignore", "azure-sev/template.gitignore")
        self.copy_template(folder, "blindbox.yml", "azure-sev/template.yml")
        self.copy_template(folder, "blindbox.tf", "azure-sev/template.tf")
    
    def build(self, *, tag: str, build_dir: t.Optional[str], source_image: str, docker_addr: t.Optional[str], **_kw):
        build_dir = self.make_blindbox_build_dir(self.cwd, build_dir)

        self.copy_template(build_dir, "Dockerfile", "azure-sev/Dockerfile")
        self.copy_template(build_dir, "sev-init.sh", "azure-sev/sev-init.sh", executable=True)
        self.copy_template(build_dir, "sev-start.sh", "azure-sev/sev-start.sh", executable=True)

        self.connect_docker_client(docker_addr)
        self.build_docker_image(build_dir, tag)
        self.close()

    def deploy(self, **_kw):
        pass

class AWSNitroBuilder(BlindBoxBuilder):
    def __init__(self,
            settings: t.Any = None,
            *,
            cwd: t.Optional[str] = None,
            **_kw
        ):
        self.settings = settings
        self.cwd = cwd

    def init_new_project(self, folder: t.Optional[str], **_kw):
        if folder is None: folder = os.getcwd()
        if folder is None: folder = self.cwd

        if not os.path.exists(folder):
            os.makedirs(folder)

        self.copy_template(folder, "blindbox.yml", "template/aws-nitro.yml")
        self.copy_template(folder, "blindbox.tf", "template/aws-nitro.tf")
    
    def build(self, *, build_directory: str, docker_image: str, **_kw):
        self.get_project_settings(self.cwd)

        self.build_docker_image(self.build_directory, self.docker_image)
        self.close()


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
        help="The directory to build the docker image from. By default, it will use the project .blindbox folder",
    )
    build_command.add_argument(
        "--source-image",
        type=str,
        help="The source docker image",
        required=True,
    )
    build_command.add_argument(
        "--docker-addr",
        type=str,
        help="The address of the docker daemon",
        # default="tcp://0.0.0.0:2375",
        default="unix:///var/run/docker.sock",
    )
    build_command.add_argument(
        "--tag",
        "-t",
        type=str,
        help="The tag to give the docker image",
        required=True
    )

    subparsers.add_parser('deploy', help="alias to `terraform apply`")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    settings = None
    if args.command == 'init':
        platform = args.platform
    else:
        settings = BlindBoxBuilder.get_project_settings(args.cwd)
        platform = settings["platform"]

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
