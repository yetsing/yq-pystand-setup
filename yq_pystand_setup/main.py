import argparse
import subprocess
import urllib.request
import os
import pathlib
import shutil
import tempfile
import zipfile


log = print

wrapper_pip_code = """#!/usr/bin/python
import sys
import os

if __name__ == "__main__":
    from pip._vendor.distlib.scripts import ScriptMaker
    ScriptMaker.executable = r"python.exe"

    from pip._internal.cli.main import main
    sys.exit(main())
"""

make_wrapper_pip_code = """
from pip._vendor.distlib.scripts import ScriptMaker
maker = ScriptMaker("runtime/pip_wrapper/scripts", "runtime/pip_wrapper/bin")
maker.executable = r"python.exe"
maker.make("pip.py")
"""

def create_empty_file(file_path: str):
    """
    Creates an empty file at the specified path.

    :param file_path: Path where the empty file will be created.
    """
    with open(file_path, 'w'):
        pass


def copy_directory(src: str, dst: str):
    """
    Copies all files from the source directory to the destination directory.

    :param src: Path to the source directory.
    :param dst: Path to the destination directory.
    """
    # Check if the source directory exists
    if not os.path.exists(src):
        raise FileNotFoundError(f"The source directory {src} does not exist.")

    # Create the destination directory if it doesn't exist
    if not os.path.exists(dst):
        os.makedirs(dst)

    # Iterate over all files and directories in the source directory
    for item in os.listdir(src):
        src_item = os.path.join(src, item)
        dst_item = os.path.join(dst, item)

        # If it's a file, copy it
        if os.path.isfile(src_item):
            shutil.copy2(src_item, dst_item)
        # If it's a directory, recursively copy it
        elif os.path.isdir(src_item):
            shutil.copytree(src_item, dst_item)


def make_project_dir(name: str) -> pathlib.Path:
    proj_dir = pathlib.Path(name).absolute()
    proj_dir.mkdir(parents=True, exist_ok=True)
    return proj_dir


def is_python_pth(filename: str) -> bool:
    return filename.startswith('python') and filename.endswith('._pth')


def update_path_pth_file(filepath: pathlib.Path):
    lines = filepath.read_text().splitlines()
    if './Lib/site-packages' in lines:
        log(f"  Skipping {filepath}")
        return
    log(f"  Updating {filepath}")
    new_lines = []
    for line in lines:
        if '# Uncomment to run site.main() automatically' in line:
            new_lines.append('./Lib/site-packages')
            new_lines.append('..')
        elif line == '#import site':
            line = line[1:]
        new_lines.append(line)
    filepath.write_text('\n'.join(new_lines))


def install_pystand(url: str, proj_dir: pathlib.Path):
    runtime_dir = proj_dir / "runtime"
    if runtime_dir.exists():
        log(f"{runtime_dir} already exists, skipping.")
        return

    log(f"  Download PyStand from {url}")
    pystand_zip_filepath, _ = urllib.request.urlretrieve(url)
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(pystand_zip_filepath) as zf:
                zf.extractall(tmpdir)
            name = os.listdir(tmpdir)[0]
            pystand_filepath = pathlib.Path(tmpdir) / name
            # remove PyStand site-packages, our package will install in runtime/Lib/site-packages
            shutil.rmtree(str(pystand_filepath / "site-packages"))
            copy_directory(str(pystand_filepath), str(proj_dir))

        for item in runtime_dir.iterdir():
            if is_python_pth(item.name):
                update_path_pth_file(item)
    finally:
        os.remove(pystand_zip_filepath)


def install_pip(proj_dir: pathlib.Path):
    url = "https://bootstrap.pypa.io/get-pip.py"
    log(f"  Download get-pip.py from {url}")
    proj_python_executable = str(proj_dir / "runtime" / "python.exe")
    get_pip_filepath, _ = urllib.request.urlretrieve(url)
    subprocess.check_call([proj_python_executable, get_pip_filepath])
    os.unlink(get_pip_filepath)

    pip_wrapper_dir = proj_dir / "runtime" / "pip_wrapper"
    (pip_wrapper_dir / "bin").mkdir(parents=True, exist_ok=True)
    (pip_wrapper_dir / "scripts").mkdir(parents=True, exist_ok=True)

    wrapper_pip_filepath = pip_wrapper_dir / "scripts" / "pip.py"
    wrapper_pip_filepath.write_text(wrapper_pip_code)
    make_pip_filepath = pip_wrapper_dir / "scripts" / "make_pip.py"
    make_pip_filepath.write_text(make_wrapper_pip_code)

    subprocess.check_call([proj_python_executable, str(make_pip_filepath)])

    activate_cmd = r"""@echo off
set PATH=%~dp0runtime\pip_wrapper\bin\;%~dp0runtime\Scripts\;%~dp0runtime\;%PATH%
"""
    (proj_dir / "activate.cmd").write_text(activate_cmd)
    activate_ps1 = r"""$ScriptDir = (Split-Path -Parent $MyInvocation.MyCommand.Definition)
$Env:PATH = "$ScriptDir\runtime\pip_wrapper\bin;$ScriptDir\runtime\Scripts;$ScriptDir\runtime;$Env:PATH"
"""
    (proj_dir / "activate.ps1").write_text(activate_ps1)


def pretend_virtualenv(proj_dir: pathlib.Path):
    filenames = [
        "activate",
        "activate.bat",
        "Activate.ps1",
        "activate_this.py"
    ]
    runtime_dir = proj_dir / "runtime"
    for filename in filenames:
        create_empty_file(str(runtime_dir / filename))


def main():
    parser = argparse.ArgumentParser(prog="PyStandSetup", description="Setup PyStand environment")
    parser.add_argument('-i', '--init', action="store_true", help="Initialize PyStand environment")
    parser.add_argument("proj_name", help="Project name")

    args = parser.parse_args()
    proj_name = args.proj_name
    if args.init:
        proj_dir = pathlib.Path(proj_name).absolute()
    else:
        log(f"Create project directory {proj_name} ...")
        proj_dir = make_project_dir(proj_name)

    os.chdir(str(proj_dir))
    log(f"Install PyStand ...")
    pystand_url = 'https://gitee.com/ayeqing/yq-file-storage/raw/master/PyStand-py38-x64.zip'
    install_pystand(pystand_url, proj_dir)
    log(f"Install pip ...")
    install_pip(proj_dir)
    log(f"Pretend virtualenv ...")
    pretend_virtualenv(proj_dir)
    log("Done.")


if __name__ == "__main__":
    main()
