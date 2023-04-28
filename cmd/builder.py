import argparse
import docker
import os
import subprocess

parser = argparse.ArgumentParser(description="Parser for the builder cli")

parser.add_argument(
    "--directory",
    type=str,
    help="The directory to build the docker image from",
    required=True,
)

parser.add_argument(
    "--tf-directory",
    type=str,
    help="The directory to run terraform apply from",
    default="tf-directory",
)

parser.add_argument(
    "--addr",
    type=str,
    help="The address of the docker daemon",
    default="tcp://0.0.0.0:2375",
)

parser.add_argument(
    "--tag",
    type=str,
    help="The tag to give the docker image",
    default="test-image",
)


class Builder:
    def __init__(
        self,
        directory: str,
        tf_directory: str = "tf-directory",
        addr: str = "tcp://0.0.0.0:2375",
        tag: str = "test-image",
    ):
        self.directory = directory
        self.addr = addr
        self.tag = tag
        self.tf_directory = tf_directory

        self.client = docker.DockerClient(base_url=addr)

    def build_docker_image(self) -> docker.models.images.Image:
        results = self.client.images.build(path=self.directory, tag=self.tag)
        image = results[0]
        for step in results[1]:
            if "stream" in step:
                print(step["stream"].strip())

        return image

    def with_tag(self, tag: str) -> "Builder":
        self.tag = tag
        return self

    def with_directory(self, directory: str) -> "Builder":
        self.directory = directory
        return self

    def with_tf_directory(self, tf_directory: str) -> "Builder":
        self.tf_directory = tf_directory
        return self

    @staticmethod
    def from_cmd(args: argparse.Namespace) -> "Builder":
        return Builder(
            directory=args.directory,
            tf_directory=args.tf_directory,
            addr=args.addr,
            tag=args.tag,
        )

    def apply(self):
        # This runs the terraform apply command to use the terraform plan
        # and apply it to the infrastructure

        try:
            # Check if the terraform directory exists
            if not os.path.exists(self.tf_directory):
                raise Exception("Terraform directory does not exist")

            # Check if the terraform binary is installed
            res = subprocess.run(
                ["terraform", "--version"],
                capture_output=True,
                text=True,
            )

            if res.returncode != 0:
                raise Exception("Terraform is not installed")

            # Run the terraform apply command
            res = subprocess.run(
                ["terraform", "apply", "-auto-approve"],
                cwd=self.tf_directory,
                capture_output=True,
                text=True,
            )

            print(res.stdout)
            print(res.stderr)

        except Exception as e:
            print(e)


if __name__ == "__main__":
    args = parser.parse_args()

    builder = Builder.from_cmd(args)

    builder.build_docker_image()
    builder.apply()
