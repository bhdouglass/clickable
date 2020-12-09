import itertools
import subprocess
import re
import json
import os
import shlex
import glob
import shutil
import inspect
from os.path import dirname, basename, isfile, join

from clickable.builders.base import Builder
from clickable.logger import logger
from clickable.exceptions import FileNotFoundException, ClickableException

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


def find(names, cwd, temp_dir=None, build_dir=None, ignore_dir=None, extensions_only=False, depth=None):
    found = []
    searchpaths = []
    searchpaths.append(cwd)

    include_build_dir = False
    if build_dir and not build_dir.startswith(os.path.realpath(cwd) + os.sep):
        include_build_dir = True
        searchpaths.append(build_dir)

    for (root, dirs, files) in itertools.chain.from_iterable(os.walk(path, topdown=True) for path in searchpaths):
        # Ignore hidden directories
        new_dirs = []
        for dir in dirs:
            if os.path.join(root, dir) == build_dir or not dir[0] == '.':
                new_dirs.append(dir)

        dirs[:] = new_dirs

        if depth:
            if include_build_dir and root.startswith(build_dir):
                if root.count(os.sep) >= (build_dir.count(os.sep) + depth):
                    del dirs[:]
            elif root.startswith(cwd):
                if root.count(os.sep) >= (cwd.count(os.sep) + depth):
                    del dirs[:]

        for name in files:
            ok = (name in names)

            if extensions_only:
                ok = any([name.endswith(n) for n in names])

            if ok:
                if ignore_dir is not None and root.startswith(ignore_dir):
                    continue

                found.append(os.path.join(root, name))

    if not found:
        raise FileNotFoundException('Could not find {}'.format(', '.join(names)))

    # Favor the manifest in the install dir first, then fall back to the build dir and finally the source dir
    file = ''
    for f in found:
        if temp_dir and f.startswith(os.path.realpath(temp_dir) + os.sep):
            file = f

    if not file:
        for f in found:
            if build_dir and f.startswith(os.path.realpath(build_dir) + os.sep):
                file = f

    if not file:
        file = found[0]

    return file


def is_command(command):
    error_code = run_subprocess_call(shlex.split('which {}'.format(command)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return error_code == 0


def check_command(command):
    if not is_command(command):
        raise ClickableException('The command "{}" does not exist on this system, please install it for clickable to work properly"'.format(command))


def env(name):
    value = None
    if name in os.environ and os.environ[name]:
        value = os.environ[name]

    return value


def get_builders():
    builder_classes = {}
    builder_dir = join(dirname(__file__), 'builders')
    modules = glob.glob(join(builder_dir, '*.py'))
    builder_modules = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

    for name in builder_modules:
        builder_submodule = __import__('clickable.builders.{}'.format(name), globals(), locals(), [name])
        for name, cls in inspect.getmembers(builder_submodule):
            if inspect.isclass(cls) and issubclass(cls, Builder) and cls.name:
                builder_classes[cls.name] = cls

    return builder_classes


def get_make_jobs_from_args(make_args):
    for arg in flexible_string_to_list(make_args):
        if arg.startswith('-j'):
            jobs_str = arg[2:]
            try:
                return int(jobs_str)
            except ValueError:
                raise ClickableException('"{}" in "make_args" is not a number, but it should be.')

    return None


def merge_make_jobs_into_args(make_args, make_jobs):
    make_jobs_arg = '-j{}'.format(make_jobs)

    if make_args:
        return '{} {}'.format(make_args, make_jobs_arg)
    else:
        return make_jobs_arg


def flexible_string_to_list(variable):
    if isinstance(variable, (str, bytes)):
        return variable.split(' ')
    return variable


def validate_clickable_json(config, schema):
    try:
        from jsonschema import validate, ValidationError
        try:
            validate(instance=config, schema=schema)
        except ValidationError as e:
            logger.error("The clickable.json configuration file is invalid!")
            error_message = e.message
            # Lets add the key to the invalid value
            if e.path:
                if len(e.path) > 1 and isinstance(e.path[-1], int):
                    error_message = "{} (in '{}')".format(error_message, e.path[-2])
                else:
                    error_message = "{} (in '{}')".format(error_message, e.path[-1])
            raise ClickableException(error_message)
    except ImportError:
        logger.warning("Dependency 'jsonschema' not found. Could not validate clickable.json.")
        pass


def image_exists(image):
    command = 'docker image inspect {}'.format(image)
    return run_subprocess_call(command,
            stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) == 0


def makedirs(path):
    os.makedirs(path, 0o777, True)
    return path


def make_absolute(path):
    if isinstance(path, list):
        return [make_absolute(p) for p in path]
    if isinstance(path, dict):
        abs_dict = {}
        for key in path:
            abs_dict[key] = make_absolute(path[key])
        return abs_dict
    return os.path.abspath(path)


def make_env_var_conform(name):
    return re.sub("[^A-Z0-9_]", "_", name.upper())


def is_sub_dir(path, parent):
    p1 = os.path.abspath(path)
    p2 = os.path.abspath(parent)
    return os.path.commonpath([p1, p2]).startswith(p2)
