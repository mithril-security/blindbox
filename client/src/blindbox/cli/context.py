import os
import pkgutil
import subprocess
import sys
import typer
import yaml
from abc import ABC
from pydantic import BaseModel
from typing import List, Literal, Optional

from .logging import log


class BlindBoxYaml(BaseModel):
    platform: Literal["azure-amd-sev", "aws-nitro"]
    image: str


class Context(ABC):
    def __init__(self, cfg: Optional[BlindBoxYaml] = None, interactive: bool = True, auto_approve: bool = False) -> None:
        super().__init__()
        self._tf_available: Optional[bool] = None
        self._docker_available: Optional[bool] = None
        self._cfg: Optional[BlindBoxYaml] = cfg
        self._interactive: bool = interactive
        self._auto_approve: bool = auto_approve

    def init_cmd(self, dir: str):
        raise NotImplementedError()

    def apply_cmd(self, dir: str):
        raise NotImplementedError()
    
    def destroy_cmd(self, dir: str):
        raise NotImplementedError()
    
    def _copy_template(
        self,
        src_package_path: str,
        dst_path: str,
        executable: bool = False,
        replace: bool = False,
        confirm_replace: bool = False,
        merge: bool = False,
    ):
        data = pkgutil.get_data(__name__, src_package_path)

        exists = os.path.exists(dst_path)

        if exists:
            if confirm_replace:
                replace = typer.confirm(f"Replace file {dst_path}?") if self._interactive else True

            if not replace and not merge:
                return

            if merge:
                with open(dst_path, "rb") as f:
                    existing_data = f.read()

                if data not in existing_data:
                    existing_data += bytes("\n", "utf-8")
                    existing_data += data
                data = existing_data

        with open(dst_path, "wb") as f:
            f.write(data)

        if executable:
            os.chmod(dst_path, 0o775)

    def _assert_tf_available(self):
        if self._tf_available is None:
            # Check if the terraform binary is installed
            res = subprocess.run(
                ["terraform", "--version"],
                capture_output=True,
                text=True,
            )

            self._tf_available = res.returncode == 0

        if not self._tf_available:
            log.error(
                "Terraform CLI was not found in PATH. Follow the instructions at [underline]https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli[/]."
            )
            exit(1)
    
    def _tf_init(self, dir: str):
        self._assert_tf_available()

        if not os.path.exists(os.path.join(dir, ".terraform")):
            self._run_subprocess(["terraform", "init"], dir=dir)

    def _tf_apply(self, dir: str, vars: dict = {}):
        self._assert_tf_available()

        args = ["terraform", "apply"]
        if not self._interactive or self._auto_approve:
            args += ["-auto-approve"]
        for k, v in vars.items():
            args += ["--var", f"{k}={v}"]

        self._run_subprocess(args, dir=dir)
    
    def _tf_destroy(self, dir: str, vars: dict = {}):
        self._assert_tf_available()

        args = ["terraform", "destroy"]
        if not self._interactive or self._auto_approve:
            args += ["-auto-approve"]
        for k, v in vars.items():
            args += ["--var", f"{k}={v}"]

        self._run_subprocess(args, dir=dir)

    def _assert_docker_available(self):
        if self._docker_available is None:
            # Check if docker is installed
            res = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
            )

            self._docker_available = res.returncode == 0

        if not self._docker_available:
            log.error(
                "Docker CLI was not found in PATH. Follow the instructions at [underline]https://docs.docker.com/engine/install[/]."
            )
            exit(1)
    
    def _run_subprocess(
        self,
        command: List[str],
        text: bool = False,
        return_stdout: bool = False,
        dir: Optional[str] = None,
        quiet: bool = False,
        assert_returncode: bool = True,
    ):
        human_readable_command = " ".join(command)
        if not quiet:
            log.info(f"Running `{human_readable_command}`...")

        try:
            res = subprocess.run(
                command,
                cwd=dir,
                stdin=sys.stdin,
                capture_output=return_stdout,
                text=text,
            )
        except KeyboardInterrupt:
            exit(1)

        if assert_returncode and res.returncode != 0:
            if return_stdout:
                log.info(f"stdout: {res.stdout}")
                log.info(f"stderr: {res.stderr}")
            log.error(
                f"Command `{human_readable_command}` terminated with non-zero return code: {res.returncode}"
            )
            exit(1)

        if return_stdout:
            return res.stdout
        
    def _load_config(self, dir: str):
        with open(os.path.join(dir, "blindbox.yml"), "rb") as file:
            dict = yaml.safe_load(file)
        self._cfg = BlindBoxYaml(**dict)
    
    def _save_config(self, dir: str):
        with open(os.path.join(dir, "blindbox.yml"), "wb") as file:
            yaml.safe_dump(dict(self._cfg), file)
    
    @staticmethod
    def from_platform(platform: str, interactive: bool = True, auto_approve: bool = False) -> "Context":
        if platform == "azure-amd-sev":
            return AzureAmdSevContext(interactive=interactive, auto_approve=auto_approve)
        elif platform == "aws-nitro":
            return AwsNitroContext(interactive=interactive, auto_approve=auto_approve)
        else:
            log.error("Invalid platform option.")
            exit(1)
    
    @staticmethod
    def from_cfg_file(dir: str, interactive: bool = True, auto_approve: bool = False) -> "Context":
        sess = Context()
        sess._load_config(dir)
        
        if sess._cfg.platform == "azure-amd-sev":
            return AzureAmdSevContext(cfg=sess._cfg, interactive=interactive, auto_approve=auto_approve)
        elif sess._cfg.platform == "aws-nitro":
            return AwsNitroContext(cfg=sess._cfg, interactive=interactive, auto_approve=auto_approve)
        else:
            log.error("Invalid platform in configuration file.")
            exit(1)


class AzureAmdSevContext(Context):
    def __init__(self, cfg: Optional[BlindBoxYaml] = None, interactive: bool = True, auto_approve: bool = False) -> None:
        super().__init__(cfg, interactive, auto_approve)

    def init_cmd(self, dir: str):
        if not os.path.exists(dir):
            os.makedirs(dir)
        
        self._copy_template("templates/azure-amd-sev/main.tf", os.path.join(dir, "main.tf"), confirm_replace=True)
        self._copy_template("templates/azure-amd-sev/outputs.tf", os.path.join(dir, "outputs.tf"), confirm_replace=True)
        self._copy_template("templates/azure-amd-sev/providers.tf", os.path.join(dir, "providers.tf"), confirm_replace=True)
        self._copy_template("templates/azure-amd-sev/variables.tf", os.path.join(dir, "variables.tf"), confirm_replace=True)
        self._copy_template("templates/azure-amd-sev/blindbox.yaml", os.path.join(dir, "blindbox.yml"), confirm_replace=True)

        log.info("Blindbox project has been initialized.")
    
    def apply_cmd(self, dir: str):
        self._load_config(dir)
        self._assert_docker_available()
        self._tf_init(dir)
        self._tf_apply(dir, { "image": self._cfg.image })

        log.info("Blindbox project has been successfully deployed.")
    
    def destroy_cmd(self, dir: str):
        self._load_config(dir)
        self._assert_docker_available()
        self._tf_destroy(dir, { "image": self._cfg.image })

        log.info("Blindbox project has been successfully destroyed.")


class AwsNitroContext(Context):
    pass
