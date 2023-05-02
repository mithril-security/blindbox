terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "us-west-2"
}

resource "aws_key_pair" "blindbox-key" {
  key_name   = "blindbox-key"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCVIwets5L820tki6qNVyV+oE7/4XFC1bwfND+gNbfDrMWtQoG8wy8sKlTzET1l/jZfz8oLLsnHZkVilDw+HxUBI4FKRUCy3JXegyMve/gU1Sj2vz0tUcGLj8vkzAQlaLLumNCbxdMvMIGKZP6ozcJqsHsFbMbOYt16zV5JcvYaszWA48pu1+EK05xkbcPYCAOyRyydV2OP0jyy0doXoolJ8/0WBU9XQZHhbIvEEN0FYaAZI0xpVRnoUaYASu/NqUKpXOOdtuBdzdgSZlxVrbQAXbvuBrYcIXGaWXWLL8uvbC1mpDrbmRwtel7juiE5IRMF2YQVBtY3ThJaqX5ZkEPj Nitro2"
}

resource "aws_security_group" "blindbox_allow_tls" {
  name = "blindbox_allow_tls"

  ingress {
    from_port        = 443
    to_port          = 443
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}

resource "aws_instance" "blindbox_server" {
  ami           = "ami-030a7ae8055f546c9"
  instance_type = "m5.xlarge"

  key_name = "blindbox-key"

  security_groups = ["blindbox_allow_tls"]

  root_block_device {
    volume_size = 128
  }

  enclave_options {
    enabled = true
  }

  user_data                   = file("init.sh")
  user_data_replace_on_change = true

  tags = {
    Name = "blindbox-test"
  }
}

output "instance_ip_address" {
  value = aws_instance.blindbox_server.public_ip
}
