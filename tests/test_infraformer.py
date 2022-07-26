from infraformer import __version__
import subprocess
import infraformer.main as infra
from os import listdir, walk
from os.path import isfile, join

BASE_DIR = "/tmp/infraformer"  # where files are generated


def test_version():
    assert __version__ == "0.1.0"


def test_create_project():
    bashCommand = f"rm -rf {BASE_DIR}"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    infra.create_project(BASE_DIR)
    files = [f for f in listdir(BASE_DIR) if isfile(join(BASE_DIR, f))]
    assert files == ["Makefile", ".gitignore"]
    assert [d[0] for d in walk(BASE_DIR)] == [
        BASE_DIR,
        f"{BASE_DIR}/terraform",
        f"{BASE_DIR}/terraform/layers",
        f"{BASE_DIR}/terraform/modules",
    ]
