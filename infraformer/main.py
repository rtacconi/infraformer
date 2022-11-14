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
from jinja2 import Environment, BaseLoader, PackageLoader, select_autoescape, FileSystemLoader

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

    with open(f"{name}/Makefile", "w+") as f:
        f.write(JINJAENV.get_template("Makefile").render(project=name))

    with open(f"{name}/.gitignore", "w+") as f:
        f.write(JINJAENV.get_template(".gitignore").render())


#template_vars was a dictionary containing all the variables
def __create_backend(base_path, stack, environ, region, project) -> str:
    environment_path = f"{base_path}/terraform/{stack}/environments/{environ}"

    if not os.path.isdir(environment_path):
        os.makedirs(environment_path)

    session_name = "{}_{}".format(stack.replace("/", "_").replace("-", "_"), environ)
    body = """bucket = "{{project}}-{{environ}}-terraform-state"
key = "{{stack}}/terraform.tfstate"
session_name = "{{session_name}}"
dynamodb_table = "{{project}}-{{environ}}-terraform-state-lock"
region = "{{region}}"
encrypt = true"""
    rtemplate = JINJAENV.from_string(body)
    rendered_body = rtemplate.render(project=project, environ=environ,
        stack=stack, session_name=session_name, region=region)

    with open(f"{environment_path}/backend.generated.tfvars", "w+") as f:
        f.write(rendered_body)

    with open(f"{environment_path}/terraform.tfvars", "w+") as f:
        f.write(
            f'''environment = "{environ}"
project = "{project}"'''
        )

    return environment_path


def create_stack(base_path, stack, environ, region) -> str:
    stack_path = f"{base_path}/terraform/{stack}"

    if not os.path.isdir(stack_path):
        os.makedirs(stack_path)

    with open(f"{base_path}/terraform.tf", "w+") as f:
        f.write(JINJAENV.get_template('terraform.tf.j2').render(region=region))

    with open(f"{base_path}/variables.tf", "w+") as f:
        f.write(JINJAENV.get_template('variables.tf.j2').render())


    empty_files = [
        f"{stack_path}/main.tf",
        f"{stack_path}/remote_state.tf",
        f"{stack_path}/outputs.tf",
    ]

    for file in empty_files:
        with open(file, "a+") as f:
            f.write("")

    return stack_path


def create_stacks(base_path, stacks, environ, region):
    for stack in stacks:
        path = f"{base_path}/{stack}"
        if not os.path.isdir(path):
            os.makedirs(path)

        create_stack(base_path, stack, environ, region)

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
    base_path = path.dirname(os.path.realpath(__file__))
    # print("Params: ", verb, command, name)

    if command == "project":
        if verb == "create":
            create_project(name)

    if command == "stack":
        if verb == "create":
            print(sys.argv)
            # __create_backend(name, sys.argv[3], sys.argv[4])
            create_stack(base_path, environ, region, layer)

if __name__ == "__main__":
    main()
