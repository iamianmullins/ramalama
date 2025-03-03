#!/usr/bin/python3

import subprocess
from pathlib import Path
import os
import errno
import sys


def main(args):
    syspath = '/usr/share/ramalama'
    sys.path.insert(0, syspath)

    import ramalama

    try:
        conman = ""
        if args[0] != "login" and args[0] != "logout":
            conman = ramalama.container_manager()
        store = ramalama.create_store()

        dryrun = False
        if len(args) < 1:
            ramalama.usage()

        while len(args) > 0:
            if args[0] == "-h" or args[0] == "--help":
                return ramalama.usage()

            if args[0] == "-v" or args[0] == "version":
                return ramalama.version()

            if args[0] == "--dryrun":
                args.pop(0)
                dryrun = True
                continue

            if args[0] in ramalama.funcDict:
                break

            ramalama.perror(f"Error: unrecognized command `{args[0]}`\n")
            ramalama.usage(1)

        port = "8080"
        host = os.getenv('RAMALAMA_HOST', port)
        if host != port:
            port = host.rsplit(':', 1)[1]

        if conman:
            home = os.path.expanduser('~')
            wd = "./ramalama"
            for p in sys.path:
                target = p+"ramalama"
                if os.path.exists(target):
                    wd = target
                    break

            conman_args = [conman, "run",
                           "--rm",
                           "-it",
                           "--security-opt=label=disable",
                           f"-v{store}:/var/lib/ramalama",
                           f"-v{home}:{home}",
                           "-v/tmp:/tmp",
                           f"-v{__file__}:/usr/bin/ramalama:ro",
                           "-e", "RAMALAMA_HOST",
                           "-e", "RAMALAMA_TRANSPORT",
                           "-p", f"{host}:{port}",
                           f"-v{wd}:{syspath}/ramalama:ro"]
            if os.path.exists("/dev/dri"):
                conman_args += ["--device", "/dev/dri"]

            if os.path.exists("/dev/kfd"):
                conman_args += ["--device", "/dev/kfd"]

            conman_args += ["quay.io/ramalama/ramalama:latest",
                            "/usr/bin/ramalama"]
            conman_args += args

            if dryrun:
                return print(*conman_args)

            ramalama.exec_cmd(conman_args)

        cmd = args.pop(0)
        ramalama.funcDict[cmd](store, args, port)
    except IndexError as e:
        ramalama.perror(str(e).strip("'"))
        sys.exit(errno.EINVAL)
    except KeyError as e:
        ramalama.perror(str(e).strip("'"))
        sys.exit(1)
    except NotImplementedError as e:
        ramalama.perror(str(e).strip("'"))
        sys.exit(errno.ENOTSUP)
    except subprocess.CalledProcessError as e:
        ramalama.perror(str(e).strip("'"))
        sys.exit(e.returncode)


if __name__ == "__main__":
    main(sys.argv[1:])
