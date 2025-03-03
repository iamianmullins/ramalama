#!/usr/bin/python3

import os
import subprocess
import tempfile
import shutil
import sys
import urllib.request


def cleanup(tmp):
    shutil.rmtree(tmp)


def available(command):
    return shutil.which(command) is not None


def nvidia_lshw():
    try:
        output = subprocess.check_output(
            ["lshw", "-c", "display", "-numeric", "-disable", "network"], text=True)
        return 'vendor: .* [10DE]' in output
    except subprocess.CalledProcessError:
        return False


def amd_lshw():
    try:
        output = subprocess.check_output(
            ["lshw", "-c", "display", "-numeric", "-disable", "network"], text=True)
        return 'vendor: .* [1002]' in output
    except subprocess.CalledProcessError:
        return False


def download(url, to):
    curl_cmd = [
        "curl", "--globoff", "--location", "--proto-default", "https",
        "-o", to, "--remote-time", "--retry", "10", "--retry-max-time", "10", url
    ]
    subprocess.run(curl_cmd, check=True)


def main():
    if sys.platform == 'darwin':
        if os.geteuid() == 0:
            print("This script is intended to run as non-root on macOS")
            sys.exit(1)
        if not available("brew"):
            print("Please install Homebrew before continuing install on macOS")
            sys.exit(2)
    elif sys.platform == 'linux':
        if os.geteuid() != 0:
            print("This script is intended to run as root on Linux")
            sys.exit(3)
    else:
        print("This script is intended to run on Linux and macOS only")
        sys.exit(4)

    bindirs = ["/opt/homebrew/bin", "/usr/local/bin", "/usr/bin", "/bin"]
    bindir = next((d for d in bindirs if d in os.environ["PATH"]), None)

    if bindir is None:
        print("No suitable bindir found in PATH")
        sys.exit(5)

    tmp_dir = tempfile.mkdtemp()
    try:
        binfile = "ramalama"
        from_file = binfile + ".py"
        host = "https://raw.githubusercontent.com"
        url = f"{host}/containers/ramalama/s/{from_file}"
        to_file = os.path.join(tmp_dir, from_file)
        download(url, to_file)
        if sys.platform == 'darwin':  # macOS
            subprocess.run(["pip3", "install", "--break-system-packages",
                           "huggingface_hub[cli]==0.24.2"], check=True)
            subprocess.run(["pip3", "install", "--break-system-packages",
                            "omlmd==0.1.4"], check=True)
            subprocess.run(["brew", "install", "llama.cpp"], check=True)

        ramalama_bin = os.path.join(bindir, binfile)
        subprocess.run(["install", "-m755", to_file, ramalama_bin], check=True)
    finally:
        cleanup(tmp_dir)


if __name__ == "__main__":
    main()
