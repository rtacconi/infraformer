import os
import sys
import shutil
from pathlib import Path
import glob
import re
import boto3
from botocore.config import Config
import botocore

sys.path.insert(0, "infraformer")
import log_builder

LOGGER = log_builder.create_logger("infraformer")
environ = "dev"
project = "msk"
region = "eu-west-1"
layer = "15_security"

def create_backend(base_path, environ, project, region, layer):
    layers_list = layer.split("_")[1:]
    body = f"""bucket = "{project}-{environ}-terraform-state"
key = "{environ}/{'-'.join(layers_list)}/terraform.tfstate"
session_name = "{'-'.join(layers_list)}"
dynamodb_table = "msk-dev-terraform-state-lock"
region = "{region}"
encrypt = true"""

    path = f"{base_path}/environments/{environ}"
    if not os.path.isdir(path):
        os.makedirs(path)
    f = open(f"{path}/terraform.tfvars", "w+")
    f.write(
        f'''environment = "{environ}"
project = "{project}"'''
    )
    f.close()

    f = open(f"{path}/backend.generated.tfvars", "w+")
    f.write(body)
    f.close()

    path = f"terraform/layers/{layer}/terraform.tf"
    f = open(path, "w+")
    f.write(
        f"""terraform {{
  required_version = "~> 1.0.6"
  backend "s3" {{}}
}}

provider "aws" {{
  region = "{region}"
}}"""
    )
    f.close()

    # Add this to variables.tf
    # variable environment {
    #   type        = string
    #   description = "The name of the environment"
    # }
    #
    # variable project {
    #   type        = string
    #   description = "The name of the project"
    # }
    empty_files = [
        f"terraform/layers/{layer}/main.tf",
        f"terraform/layers/{layer}/variables.tf",
        f"terraform/layers/{layer}/outputs.tf",
    ]
    for file in empty_files:
        f = open(file, "a")
        f.write("")
        f.close()


def create_layers(base_path, environ, project, region):
    layers = [
        "07_secrets",
        "10_network",
        "18_database",
        "30_compute",
        "40_frontend"
    ]

    for layer in layers:
        path = f"{base_path}/{layer}"
        if not os.path.isdir(path):
            os.makedirs(path)
            create_backend(path, environ, project, region, layer)

base_path = "terraform/layers"
create_layers(base_path, environ, project, region)

def remove_layers(layers):
    [shutil.rmtree(f"{base_path}/{l}") for l in layers]


def create_bucket(bucket_name, region):
    session = boto3.Session(region_name=region)
    client = session.client("s3")
    client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={"LocationConstraint": region},
    )
    response = client.put_bucket_encryption(
        Bucket=bucket_name,
        # ContentMD5='string',
        ServerSideEncryptionConfiguration={
            "Rules": [
                {"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}},
            ]
        },
    )


def delete_bucket(bucket_name):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    exists = True

    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            exists = False

    if exists:
        for key in bucket.objects.all():
            key.delete()
        bucket.delete()
    else:
        LOGGER.info("Bucket not found")


def main():
    task = sys.argv[1]

    if task == "create-layer":
        create_backend()


if __name__ == "__main__":
    main()



create_backend(path, environ, project, region, layer)
