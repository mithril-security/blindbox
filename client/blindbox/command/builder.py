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
from pydantic import BaseModel, Field
import pydantic
import inquirer
from rich import table, console

info_console = console.Console(file=sys.stdout, highlight=False)
error_console = console.Console(file=sys.stderr, highlight=False)


def info(text, **kwargs):
    info_console.print(
        "[white]\[blindbox] [bold]>[/bold][/white] [green]" + text,
        **kwargs,
    )


def error_exit(text, **kwargs):
    error_console.print(
        "[red bold]Error[/red bold][white]: " + text,
        **kwargs,
    )
    exit(1)


IPModel = pydantic.constr(regex="^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")


class BlindBoxYml(BaseModel):
    platform: t.Literal["azure-sev", "aws-nitro"]
    ip_rules: t.List[IPModel] = Field(alias="ip-rules", default=[])
    dns_ip_rules: t.List[IPModel] = Field(
        alias="dns-ip-rules", default=["168.63.129.16"]
    )


class BlindBoxBuilder(abc.ABC):
    interactive_mode: bool = True

    def yes_no_question(self, text: str):
        if not self.interactive_mode:
            return None
        answers = inquirer.prompt([inquirer.Confirm("answer", message=text)])
        if not answers:  # CTRL+C
            exit(1)
        return answers["answer"]

    def run_subprocess(
        self,
        command: t.List[str],
        *,
        text: bool = False,
        return_stdout: bool = False,
        cwd: t.Optional[str] = None,
        quiet: bool = False,
        assert_returncode: bool = True,
    ):
        human_readable = " ".join(command)
        if not quiet:
            info(f"Running `{human_readable}`...")

        capture_output = return_stdout
        try:
            res = subprocess.run(
                command,
                cwd=cwd,
                stdin=sys.stdin,
                capture_output=capture_output,
                text=text,
            )
        except KeyboardInterrupt:
            exit(1)

        if assert_returncode and res.returncode != 0:
            if capture_output:
                info("stdout:")
                info_console.print(res.stdout)
                info("stderr:")
                info_console.print(res.stderr)
            error_exit(
                f"Command `{human_readable}` terminated with non-zero return code: {res.returncode}"
            )

        if return_stdout:
            return res.stdout

    def make_blindbox_build_dir(
        self, project_folder: t.Optional[str] = None, build_dir: t.Optional[str] = None
    ):
        if project_folder is None:
            project_folder = "."
        if build_dir is None:
            build_dir = path.join(project_folder, ".blindbox")

        if not path.exists(build_dir):
            os.makedirs(build_dir)

        return build_dir

    @staticmethod
    def get_project_settings(project_folder: t.Optional[str] = None) -> BlindBoxYml:
        if project_folder is None:
            project_folder = "."
        with open(path.join(project_folder, "blindbox.yml"), "rb") as file:
            dict = yaml.safe_load(file)
        return BlindBoxYml(**dict)

    @staticmethod
    def save_project_settings(
        settings: BlindBoxYml, project_folder: t.Optional[str] = None
    ):
        if project_folder is None:
            project_folder = "."
        with open(path.join(project_folder, "blindbox.yml"), "wb") as file:
            yaml.safe_dump(
                settings.dict(),
                file,
                encoding="utf-8",
            )

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
            error_exit(
                "Terraform CLI was not found in PATH. Follow the instructions at [underline]https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli[/]."
            )

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
            error_exit(
                "Docker CLI was not found in PATH. Follow the instructions at [underline]https://docs.docker.com/engine/install[/]."
            )

    def export_docker_image(self, tag: str, target_file: str):
        self.assert_docker_available()
        self.run_subprocess(["docker", "save", tag, "-o", target_file])

    def build_docker_image(self, build_dir: str, tag: str, *, buildargs: dict = {}):
        self.assert_docker_available()
        args = ["docker", "build", "-t", tag]
        for k, v in buildargs.items():
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
        for k, v in vars.items():
            args += ["--var", f"{k}={v}"]

        self.run_subprocess(args, cwd=dir)

    def copy_template(
        self,
        folder: str,
        file: str,
        package_path: str,
        *,
        executable: bool = False,
        replace: bool = False,
        confirm_replace: bool = False,
        merge: bool = False,
    ):
        data = pkgutil.get_data(__name__, package_path)
        file = path.join(folder, file)

        exists = path.exists(file)

        if exists:
            if confirm_replace:
                replace = self.yes_no_question(f"Replace file {file}")

            if not replace and not merge:
                return

            if merge:
                with open(file, "rb") as f:
                    existing_data = f.read()

                if data not in existing_data:
                    existing_data += bytes("\n", "utf-8")
                    existing_data += data
                data = existing_data

        with open(file, "wb") as f:
            f.write(data)

        if executable:
            os.chmod(file, 0o775)

    def init_new_project(self, folder: t.Optional[str], **_kw):
        raise NotImplementedError()

    def build(self, **_kw):
        raise NotImplementedError()

    def deploy(self, **_kw):
        raise NotImplementedError()


class AzureSEVBuilder(BlindBoxBuilder):
    def __init__(
        self, settings: BlindBoxYml = None, *, cwd: t.Optional[str] = None, **_kw
    ):
        self.settings = settings
        self.cwd = cwd

    def init_new_project(self, folder: t.Optional[str], **_kw):
        if folder is None:
            folder = "."
        if folder is None:
            folder = self.cwd

        if not os.path.exists(folder):
            os.makedirs(folder)

        self.copy_template(
            folder,
            ".gitignore",
            "azure-sev/template.gitignore",
            merge=True,
        )
        self.copy_template(
            folder, "blindbox.yml", "azure-sev/template.yml", confirm_replace=True
        )
        self.copy_template(
            folder, "blindbox.tf", "azure-sev/template.tf", confirm_replace=True
        )

        info("[green bold]Blindbox project has been initialized!")

    def populate_iplist(self, build_dir):
        ips = [*self.settings.dns_ip_rules, *self.settings.ip_rules]

        with open(path.join(build_dir, "sev-start.sh"), "r+") as rewrite:
            lines = rewrite.readlines()
            rewrite.seek(0)
            for line in lines:
                if line.startswith("# iptables rules inserted from CLI"):
                    for x in ips:
                        line += (
                            "iptables -I DOCKER-USER -d "
                            + x
                            + " -i docker0 -j ACCEPT"
                            + "\n"
                        )
                rewrite.write(line)
        return ips

    def build(
        self,
        *,
        tag: str,
        build_dir: t.Optional[str],
        source_image: str,
#        save: bool,
        **_kw,
    ):
        build_dir = self.make_blindbox_build_dir(self.cwd, build_dir)

        self.copy_template(build_dir, "Dockerfile", "azure-sev/Dockerfile", replace=True)
        self.copy_template(
            build_dir, "sev-init.sh", "azure-sev/sev-init.sh", executable=True, replace=True
        )
        self.copy_template(
            build_dir, "sev-start.sh", "azure-sev/sev-start.sh", executable=True, replace=True
        )

        info("Inserting allowed IPs...")
        ips = self.populate_iplist(build_dir)
        tab = table.Table(box=table.box.SIMPLE)
        tab.add_column("Allowed IPs")
        for ip in ips:
            if ip in self.settings.dns_ip_rules:
                ip += " (DNS)"
            tab.add_row(ip)
        info_console.print(tab)

        self.export_docker_image(
            source_image, path.join(build_dir, source_image + ".tar")
        )
        self.build_docker_image(
            build_dir, tag, buildargs={"EMBED_IMAGE_TAR": source_image + ".tar"}
        )

        image_hash = self.docker_get_image_hash(tag)
        info(
            f"[green bold]Successfully built image with hash: [/green bold][cyan]{image_hash}"
        )

    def deploy(self, image: t.Optional[str], **_kw):
        folder = self.cwd
        if folder is None:
            folder = "."
        self.assert_tf_available()

        self.tf_init_if_necessary(folder)
        self.tf_apply(folder, {"image": image})

        info("[green bold]Blindbox project has been successfully deployed.")


class AWSNitroBuilder(BlindBoxBuilder):
    def __init__(
        self, settings: BlindBoxYml = None, *, cwd: t.Optional[str] = None, **_kw
    ):
        self.settings = settings
        self.cwd = cwd

    def init_new_project(self, folder: t.Optional[str], **_kw):
        if folder is None:
            folder = "."
        if folder is None:
            folder = self.cwd

        if not os.path.exists(folder):
            os.makedirs(folder)

        self.copy_template(folder, "blindbox.yml", "template/aws-nitro.yml")
        self.copy_template(folder, "blindbox.tf", "template/aws-nitro.tf")

    def build(self, *, build_directory: str, docker_image: str, **_kw):
        pass


def main():
    parser = argparse.ArgumentParser(description="Parser for the builder cli")
    parser.add_argument("--cwd", "-C", help="manually specify the project root")
    parser.add_argument(
        "--platform",
        choices=["azure-sev", "aws-nitro"],
        help="override the used platform",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="disable interactive prompting, for use in shell scripts",
    )
    subparsers = parser.add_subparsers(dest="command")

    init_command = subparsers.add_parser("init", help="initialize a blindbox project")
    init_command.add_argument(
        "--folder",
        "-f",
        default=".",
    )

    build_command = subparsers.add_parser("build", help="build a blindbox")
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
        "--tag",
        "-t",
        type=str,
        help="the tag to give the newly built docker image",
        required=True,
    )

    deploy_command = subparsers.add_parser("deploy", help="alias to `terraform apply`")
    deploy_command.add_argument(
        "image",
        type=str,
        help="the image to deploy. Build it first using `blindbox build`.",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        exit(1)

    settings: t.Optional[BlindBoxYml] = None
    if args.command == "init":
        platform = args.platform

        if platform is None:
            if args.non_interactive:
                error_exit("Please supply a --platform to init the project.")
            else:
                answers = inquirer.prompt(
                    [
                        inquirer.List(
                            "platform",
                            "Select the platform to use",
                            choices=[
                                "azure-sev - AMD-SEV SNP on Azure Cloud via ACI containers",
                                "aws-nitro - Nitro containers on Amazon Web Services",
                            ],
                        )
                    ]
                )
                if not answers:  # CTRL+C
                    exit(1)

                if "azure-sev" in answers["platform"]:
                    platform = "azure-sev"
                else:
                    platform = "aws-nitro"
    else:
        settings = BlindBoxBuilder.get_project_settings(args.cwd)
        platform = settings.platform

    if platform == "aws-nitro":
        builder = AWSNitroBuilder(settings, **args.__dict__)
    else:
        builder = AzureSEVBuilder(settings, **args.__dict__)

    if args.command == "init":
        builder.init_new_project(**args.__dict__)
    elif args.command == "build":
        builder.build(**args.__dict__)
    elif args.command == "deploy":
        builder.deploy(**args.__dict__)

    return 0


if __name__ == "__main__":
    sys.exit(main())
