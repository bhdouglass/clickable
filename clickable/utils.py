import itertools
import subprocess
import json
import os
import shlex


# TODO use these subprocess functions everywhere

def run_subprocess_call(cmd, **args):
    if isinstance(cmd, str):
        cmd = cmd.encode()
    elif isinstance(cmd, (list, tuple)):
        for idx, x in enumerate(cmd):
            if isinstance(x, str):
                cmd[idx] = x.encode()
    return subprocess.call(cmd, **args)


def run_subprocess_check_output(cmd, **args):
    if isinstance(cmd, str):
        cmd = cmd.encode()
    elif isinstance(cmd, (list, tuple)):
        for idx, x in enumerate(cmd):
            if isinstance(x, str):
                cmd[idx] = x.encode()
    return subprocess.check_output(cmd, **args).decode()


class Colors:
    INFO = '\033[94m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    CLEAR = '\033[0m'


def print_info(message):
    print(Colors.INFO + message + Colors.CLEAR)


def print_success(message):
    print(Colors.SUCCESS + message + Colors.CLEAR)


def print_warning(message):
    print(Colors.WARNING + message + Colors.CLEAR)


def print_error(message):
    print(Colors.ERROR + message + Colors.CLEAR)


class ManifestNotFoundException(Exception):
    pass


def find_manifest(cwd, temp_dir=None, build_dir=None):
    manifests = []
    searchpaths = []
    searchpaths.append(cwd)

    if build_dir and not build_dir.startswith(os.path.realpath(cwd) + os.sep):
        searchpaths.append(build_dir)

    for (root, dirs, files) in itertools.chain.from_iterable(os.walk(path, topdown=True) for path in searchpaths):
        for name in files:
            if name == 'manifest.json':
                manifests.append(os.path.join(root, name))

    if not manifests:
        raise ManifestNotFoundException('Could not find manifest.json')

    # Favor the manifest in the install dir first, then fall back to the build dir and finally the source dir
    manifest = ''
    for m in manifests:
        if temp_dir and m.startswith(os.path.realpath(temp_dir) + os.sep):
            manifest = m

    if not manifest:
        for m in manifests:
            if build_dir and m.startswith(os.path.realpath(build_dir) + os.sep):
                manifest = m

    if not manifest:
        manifest = manifests[0]

    return manifest


def get_manifest(cwd, temp_dir=None, build_dir=None):
    manifest = {}
    with open(find_manifest(cwd, temp_dir, build_dir), 'r') as f:
        try:
            manifest = json.load(f)
        except ValueError:
            raise ValueError('Failed reading "manifest.json", it is not valid json')

    return manifest


def check_command(command):
    error_code = run_subprocess_call(shlex.split('which {}'.format(command)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if error_code != 0:
        raise Exception('The command "{}" does not exist on this system, please install it for clickable to work properly"'.format(command))
