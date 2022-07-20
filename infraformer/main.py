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


def create_backend(base_path, environ, project, region, layer):
    # layers_list = layer.split("_")[1:]
    environment_path = f"{base_path}/terraform/layers/{layer}/environments/{environ}"

    if not os.path.isdir(environment_path):
        os.makedirs(environment_path)

    body = f"""bucket = "{project}-{environ}-terraform-state"
key = "{environ}/{layer}/terraform.tfstate"
session_name = "{layer}"
dynamodb_table = "msk-dev-terraform-state-lock"
region = "{region}"
encrypt = true"""
    f = open(f"{environment_path}/backend.generated.tfvars", "w+")
    f.write(body)
    f.close()

    f = open(f"{environment_path}/terraform.tfvars", "w+")
    f.write(
        f'''environment = "{environ}"
project = "{project}"'''
    )
    f.close()


def create_layer(base_path, environ, project, region, layer):
    layer_path = f"{base_path}/terraform/layers/{layer}"

    if not os.path.isdir(layer_path):
        os.makedirs(layer_path)

    path = f"{layer_path}/terraform.tf"
    f = open(path, "w+")
    f.write(
        f"""terraform {{
  required_version = "~> 1.0.6"
  backend "s3" {{}}
}}

provider "aws" {{
  region = "{region}"
}}
"""
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
        f"{layer_path}/main.tf",
        f"{layer_path}/variables.tf",
        f"{layer_path}/outputs.tf",
    ]
    for file in empty_files:
        f = open(file, "a")
        f.write("")
        f.close()

    create_backend(base_path, environ, project, region, layer)


def create_layers(base_path, environ, project, region):
    layers = ["07_secrets", "10_network", "18_database", "30_compute", "40_frontend"]

    for layer in layers:
        path = f"{base_path}/{layer}"
        if not os.path.isdir(path):
            os.makedirs(path)
            create_backend(path, environ, project, region, layer)


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
    environ = "dev"
    project = "msk"
    region = "eu-west-1"
    layer = "15_security"

    if task == "create-layer":
        create_backend("/tmp", environ, project, region, layer)


if __name__ == "__main__":
    main()


create_layer("/tmp", environ, project, region, layer)

path = f"/tmp/environments/{environ}"
if not os.path.isdir(path):
    os.makedirs(path)
