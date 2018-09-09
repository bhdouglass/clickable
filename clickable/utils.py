import itertools
import subprocess
import json
import os
import shlex


# TODO make this into different classes, Print, Subprocess, Device, etc


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


def detect_devices():
    output = run_subprocess_check_output(shlex.split('adb devices -l')).strip()
    devices = []
    for line in output.split('\n'):
        if 'device' in line and 'devices' not in line:
            device = line.split(' ')[0]
            for part in line.split(' '):
                if part.startswith('model:'):
                    device = '{} - {}'.format(device, part.replace('model:', '').replace('_', ' ').strip())

            devices.append(device)

    return devices


def check_any_devices():
    devices = detect_devices()
    if len(devices) == 0:
        raise Exception('No devices available via adb')


def check_multiple_devices(device_serial_number):
    devices = detect_devices()
    if len(devices) > 1 and not device_serial_number:
        raise Exception('Multiple devices detected via adb')


def run_device_command(command, config, cwd=None):
    if config.container_mode:
        print_warning('Skipping device command, running in container mode')
        return

    if not cwd:
        cwd = config.dir

    wrapped_command = ''
    if config.ssh:
        wrapped_command = 'echo "{}" | ssh phablet@{}'.format(command, config.ssh)
    else:
        check_any_devices()

        if config.device_serial_number:
            wrapped_command = 'adb -s {} shell "{}"'.format(config.device_serial_number, command)
        else:
            check_multiple_devices(config.device_serial_number)
            wrapped_command = 'adb shell "{}"'.format(command)

    subprocess.check_call(wrapped_command, cwd=cwd, shell=True)


def check_command(command):
    error_code = run_subprocess_call(shlex.split('which {}'.format(command)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if error_code != 0:
        raise Exception('The command "{}" does not exist on this system, please install it for clickable to work properly"'.format(command))
