from infraformer import __version__
import subprocess
import infraformer.main as infra
from os import listdir, walk, path, mkdir, system
from os.path import isfile, join

BASE_DIR = "/tmp/infraformer"  # where files are generated

def test_version():
    assert __version__ == "0.1.0"


def test_create_project():
    if path.isdir(BASE_DIR):
        system(f"rm -rf {BASE_DIR}/*")
    else:
        mkdir(BASE_DIR)


    infra.create_project(BASE_DIR)
    files = [f for f in listdir(BASE_DIR) if isfile(join(BASE_DIR, f))]
    assert "Makefile" in files
    assert ".gitignore" in files
    dirs = [d[0] for d in walk(BASE_DIR)]
    assert BASE_DIR in dirs
    assert f"{BASE_DIR}/terraform" in dirs
    assert f"{BASE_DIR}/terraform/modules" in dirs


def test_create_stack():
    if path.isdir(BASE_DIR):
        system(f"rm -rf {BASE_DIR}/*")
    else:
        mkdir(BASE_DIR)

    result = infra.create_stack(BASE_DIR, "eu-west-1/15_security", "dev", "eu-west-2")
    # assert result == f"{BASE_DIR}/terraform/eu-west-1/15_security"
    # files = [f for f in listdir(result) if isfile(join(result, f))]
    # assert files == [
    #     "outputs.tf",
    #     "main.tf",
    #     "remote_state.tf",
    #     "variables.tf",
    #     "terraform.tf",
    # ]
    # assert [d[0] for d in walk(f"{BASE_DIR}/terraform/layers/15_security")] == [
    #     "/tmp/infraformer/terraform/eu-west-1/15_security",
    #     "/tmp/infraformer/terraform/eu-west-1/15_security/environments",
    #     "/tmp/infraformer/terraform/eu-west-1/15_security/environments/dev",
    # ]

def test_create_stack_with_eu_west_2():
    if path.isdir(BASE_DIR):
        system(f"rm -rf {BASE_DIR}/*")
    else:
        mkdir(BASE_DIR)

    #result = infra.create_stack(BASE_DIR, "eu-west-1/15_security", "dev", "eu-west-2")
    #assert ..... == "eu-west-2"

def test_create_backend():
    if path.isdir(BASE_DIR):
        system(f"rm -rf {BASE_DIR}/*")
    else:
        mkdir(BASE_DIR)

    #infra.create_stack(BASE_DIR, "eu-west-1/15_security", "dev", "eu-west-2")
    infra.__create_backend(BASE_DIR, "eu-west-1/15_security", "dev", "eu-west-2", "infraformer")
    p = infra.__create_backend(BASE_DIR, "eu-west-1/15_security", "dev", "eu-west-2", "infraformer")
    content = open(f"{p}/backend.generated.tfvars", "r").read()

    assert "infraformer-dev-terraform-state" in content

def test_create_stacks():
    stacks = ["07_secrets", "10_network", "18_database", "30_compute", "40_frontend"]
    result = infra.create_stacks(BASE_DIR, stacks, "dev", "eu-west-2")
