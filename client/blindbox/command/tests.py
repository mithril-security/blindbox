import unittest
import docker
from builder import AWSNitroBuilder, parser


class TestBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = AWSNitroBuilder(directory="test_dir")

    def test_build_docker_image(self):
        client = docker.from_env()
        self.assertEqual(
            self.builder.build_docker_image(), client.images.get("test-image")
        )
        client.close()

    def test_build_docker_image_with_tag(self):
        client = docker.from_env()
        self.assertEqual(
            self.builder.with_tag("test-new-tag").build_docker_image(),
            client.images.get("test-new-tag"),
        )
        client.close()

    def test_build_docker_image_with_directory(self):
        # Throw an error if the directory doesn't exist
        with self.assertRaises(TypeError) as context:
            self.builder.with_directory("nonexistent_dir").build_docker_image()

    def test_terraform_apply(self):
        self.builder.with_tf_directory("test-tf").apply()

    def test_builder_from_cmd_with_parser(self):
        args = parser.parse_args(
            [
                "--directory",
                "test_dir",
                "--tf-directory",
                "test-tf",
            ]
        )

        self.builder = AWSNitroBuilder.from_cmd(args)
        self.assertEqual(self.builder.directory, "test_dir")
        self.test_build_docker_image()
        self.test_terraform_apply()
        self.builder.client.close()

    def tearDown(self) -> None:
        def delete_image(image: str):
            try:
                self.builder.client.images.remove(image)
            except docker.errors.ImageNotFound:
                pass

        [delete_image(image) for image in ["test-image", "test-new-tag"]]
        self.builder.client.close()

        return super().tearDown()
