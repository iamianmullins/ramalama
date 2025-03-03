import os
import re
from ramalama import *
from ramalama.common import run_cmd
from ramalama.model import Model


def download(ramalama_store, model, directory, filename):
    return run_cmd(["huggingface-cli", "download", directory, filename, "--cache-dir", ramalama_store + "/repos/huggingface/.cache", "--local-dir", ramalama_store + "/repos/huggingface/" + directory])


def try_download(ramalama_store, model, directory, filename):
    proc = download(ramalama_store, model, directory, filename)
    return proc.stdout.decode('utf-8')


class Huggingface(Model):
    def __init__(self, model):
        super().__init__(model.removeprefix("huggingface://"))
        self.type = "HuggingFace"

    def login(self, args):
        conman_args = ["huggingface-cli", "login"]
        if args.token:
            conman_args.extend(["--token", args.token])
        exec_cmd(conman_args)

    def logout(self, args):
        conman_args = ["huggingface-cli", "logout"]
        if args.token:
            conman_args.extend(["--token", args.token])
        conman_args.extend(args)
        exec_cmd(conman_args)

    def pull(self, store):
        split = self.model.rsplit('/', 1)
        directory = ""
        if len(split) > 1:
            directory = split[0]
            filename = split[1]
        else:
            filename = split[0]

        gguf_path = try_download(store, self.model, directory, filename)
        directory = f"{store}/models/huggingface/{directory}"
        os.makedirs(directory, exist_ok=True)
        symlink_path = f"{directory}/{filename}"
        relative_target_path = os.path.relpath(
            gguf_path.rstrip(), start=os.path.dirname(symlink_path))
        if os.path.exists(symlink_path) and os.readlink(symlink_path) == relative_target_path:
            # Symlink is already correct, no need to update it
            return symlink_path

        run_cmd(["ln", "-sf", relative_target_path, symlink_path])

        return symlink_path
