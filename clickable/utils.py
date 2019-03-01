import itertools
import subprocess
import json
import os
import shlex
import glob
import inspect
from os.path import dirname, basename, isfile, join

from clickable.build_templates.base import Builder

# TODO use these subprocess functions everywhere


def prepare_command(cmd, shell=False):
    if isinstance(cmd, str):
        if shell:
            cmd = cmd.encode()
        else:
            cmd = shlex.split(cmd)

    if isinstance(cmd, (list, tuple)):
        for idx, x in enumerate(cmd):
            if isinstance(x, str):
                cmd[idx] = x.encode()

    return cmd


def run_subprocess_call(cmd, shell=False, **args):
    return subprocess.call(prepare_command(cmd, shell), shell=shell, **args)


def run_subprocess_check_call(cmd, shell=False, cwd=None, **args):
    return subprocess.check_call(prepare_command(cmd, shell), shell=shell, cwd=cwd, **args)


def run_subprocess_check_output(cmd, shell=False, **args):
    return subprocess.check_output(prepare_command(cmd, shell), shell=shell, **args).decode()


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


def find_manifest(cwd, temp_dir=None, build_dir=None, ignore_dir=None):
    manifests = []
    searchpaths = []
    searchpaths.append(cwd)

    if build_dir and not build_dir.startswith(os.path.realpath(cwd) + os.sep):
        searchpaths.append(build_dir)

    for (root, dirs, files) in itertools.chain.from_iterable(os.walk(path, topdown=True) for path in searchpaths):
        for name in files:
            if name == 'manifest.json':
                if ignore_dir is not None and root.startswith(ignore_dir):
                    continue

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


def env(name):
    value = None
    if name in os.environ and os.environ[name]:
        value = os.environ[name]

    return value


def get_builders():
    builder_classes = {}
    builder_dir = join(dirname(__file__), 'build_templates')
    modules = glob.glob(join(builder_dir, '*.py'))
    builder_modules = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

    for name in builder_modules:
        builder_submodule = __import__('clickable.build_templates.{}'.format(name), globals(), locals(), [name])
        for name, cls in inspect.getmembers(builder_submodule):
            if inspect.isclass(cls) and issubclass(cls, Builder) and cls.name:
                builder_classes[cls.name] = cls

    return builder_classes


def merge_make_jobs_into_args(make_args=None, make_jobs=0):
    make_args_contains_jobs = make_args and any([arg.startswith('-j') for arg in make_args])

    if make_args_contains_jobs:
        if make_jobs:
            raise ValueError('Conflict: Number of make jobs has been specified by both, "make_args" and "make_jobs"!')
        else:
            return make_args
    else:
        make_jobs_arg = '-j'
        if make_jobs:
            make_jobs_arg = '{}{}'.format(make_jobs_arg, make_jobs)

        if make_args:
            return '{} {}'.format(make_args, make_jobs_arg)
        else:
            return make_jobs_arg


def flexible_string_to_list(variable):
    if isinstance(variable, (str, bytes)):
        return variable.split(' ')
    return variable
