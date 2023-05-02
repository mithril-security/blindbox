from dataclasses import dataclass


@dataclass
class TerraformConfig:
    instance_type: str = "m5.xlarge"
    public_key: str
    volume_size: int


def generate_terraform_config_file(config: TerraformConfig) -> str:
    return f"""
"""
