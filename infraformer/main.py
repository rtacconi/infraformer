import os
import sys
import types
import shutil
from pathlib import Path
import glob
import re
import boto3
from botocore.config import Config
import botocore
from jinja2 import Environment, BaseLoader, PackageLoader, select_autoescape

# sys.path.insert(0, "infraformer")
# import log_builder
#
# LOGGER = log_builder.create_logger("infraformer")
JINJAENV = Environment(
    loader=PackageLoader("infraformer"), autoescape=select_autoescape()
)


def create_project(name) -> str:
    terraform_path = f"{name}/terraform"

    dirs = [terraform_path, f"{terraform_path}/modules"]

    for dir in dirs:
        if not os.path.isdir(dir):
            os.makedirs(dir)

    f = open(f"{name}/Makefile", "w+")
    f.write(JINJAENV.get_template("Makefile").render(project=name))
    f.close()
    f = open(f"{name}/.gitignore", "w+")
    f.write(JINJAENV.get_template(".gitignore").render())
    f.close()


def __create_backend(template_vars) -> str:
    environment_path = f"{template_vars['base_path']}/terraform/layers/{template_vars['layer']}/environments/{template_vars['environ']}"

    if not os.path.isdir(environment_path):
        os.makedirs(environment_path)

    body = """bucket = "{{v.project}}-{{v.environ}}-terraform-state"
    key = "{{v.environ}}/{{v.layer}}/terraform.tfstate"
    session_name = "{{v.layer}}"
    dynamodb_table = "msk-dev-terraform-state-lock"
    region = "{{v.region}}"
    encrypt = true"""
    rtemplate = JINJAENV.from_string(body)
    rendered_body = rtemplate.render(v=template_vars)
    f = open(f"{environment_path}/backend.generated.tfvars", "w+")
    f.write(rendered_body)
    f.close()

    f = open(f"{environment_path}/terraform.tfvars", "w+")
    f.write(
        f'''environment = "{template_vars['environ']}"
project = "{template_vars['project']}"'''
    )
    f.close()

    return environment_path


def create_stack(base_path, environ, project, region, layer) -> str:
    v = {
        "base_path": base_path,
        "environ": environ,
        "project": project,
        "region": region,
        "layer": layer,
    }
    layer_path = f"{base_path}/terraform/layers/{layer}"

    if not os.path.isdir(layer_path):
        os.makedirs(layer_path)

    path = f"{layer_path}/terraform.tf"
    body = """terraform {{
    required_version = "~> 1.0.6"
    backend "s3" {{}}
    }}

    provider "aws" {{
    region = "{{region}}"
    }}
    """
    rtemplate = JINJAENV.from_string(body)
    rendered_body = rtemplate.render(v=template_vars)
    path = f"{layer_path}/variables.tf"
    f.write(rendered_body)
    f.close()

    body = f"""
    variable environment {{
    type        = string
    description = "The name of the environment"
    }}

    variable project {{
    type        = string
    description = "The name of the project"
    }}
    """

    rtemplate = JINJAENV.from_string(body)
    rendered_body = rtemplate.render(v=template_vars)
    path = f"{layer_path}/variables.tf"
    f.write(rendered_body)
    f.close()

    empty_files = [
        f"{layer_path}/main.tf",
        f"{layer_path}/remote_state.tf",
        f"{layer_path}/outputs.tf",
    ]
    for file in empty_files:
        f = open(file, "a")
        f.write("")
        f.close()

    __create_backend(v)

    return layer_path


def create_stacks(base_path, environ, project, region):
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
    verb = sys.argv[1]
    command = sys.argv[2]
    name = sys.argv[3]
    # print("Params: ", verb, command, name)

    if command == "project":
        if verb == "create":
            create_project(name)

    if command == "stack":
        if verb == "create":
            print(sys.argv)
            __create_backend(name, sys.argv[3], sys.argv[4])


if __name__ == "__main__":
    main()
