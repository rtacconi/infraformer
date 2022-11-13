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


# def test_create_layer():
#     bashCommand = f"rm -rf {BASE_DIR}"
#     process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
#     result = infra.create_layer(BASE_DIR, "dev", "msk", "eu-west-1", "15_security")
#     assert result == f"{BASE_DIR}/terraform/layers/15_security"
#     files = [f for f in listdir(result) if isfile(join(result, f))]
#     assert files == [
#         "outputs.tf",
#         "main.tf",
#         "remote_state.tf",
#         "variables.tf",
#         "terraform.tf",
#     ]
#     assert [d[0] for d in walk(f"{BASE_DIR}/terraform/layers/15_security")] == [
#         "/tmp/infraformer/terraform/layers/15_security",
#         "/tmp/infraformer/terraform/layers/15_security/environments",
#         "/tmp/infraformer/terraform/layers/15_security/environments/dev",
#     ]
