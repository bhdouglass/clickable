import os

from clickable.utils import (
    merge_make_jobs_into_args,
    flexible_string_to_list,
)
from clickable.exceptions import ClickableException
from clickable.logger import logger
from collections import OrderedDict


class LibConfig(object):
    cwd = os.getcwd()
    config = {}

    QMAKE = 'qmake'
    CMAKE = 'cmake'
    CUSTOM = 'custom'

    arch_triplet_mapping = {
        'armhf': 'arm-linux-gnueabihf',
        'arm64': 'aarch64-linux-gnu',
        'amd64': 'x86_64-linux-gnu',
        'all': 'all'
    }

    container_mapping = {
        ('16.04', 'armhf'): 'clickable/ubuntu-sdk:16.04-armhf',
        ('16.04', 'amd64'): 'clickable/ubuntu-sdk:16.04-amd64',
        ('16.04', 'amd64-nvidia'): 'clickable/ubuntu-sdk:16.04-amd64-nvidia',
        ('16.04', 'arm64'): 'clickable/ubuntu-sdk:16.04-arm64',
    }

    container_list = list(container_mapping.values())

    placeholders = OrderedDict({
        "ARCH_TRIPLET": "arch_triplet",
        "NAME": "name",
        "ROOT": "root_dir",
        "BUILD_DIR": "build_dir",
        "SRC_DIR": "src_dir",
        "INSTALL_DIR": "install_dir",
    })
    accepts_placeholders = ["root_dir", "build_dir", "src_dir", "install_dir",
                            "build", "build_args", "make_args", "postmake",
                            "postbuild", "prebuild"]

    path_keys = ['root_dir', 'build_dir', 'src_dir', 'install_dir']
    required = ['template']
    flexible_lists = ['dependencies_host', 'dependencies_target',
                      'dependencies_ppa', 'dependencies_build',
                      'build_args', 'make_args']
    templates = [QMAKE, CMAKE, CUSTOM]

    first_docker_info = True
    container_mode = False
    use_nvidia = False
    custom_docker_image = False
    gopath = None

    def __init__(self, name, json_config, arch, root_dir, debug_build):
        # Must come after ARCH_TRIPLET to avoid breaking it
        self.placeholders.update({"ARCH": "arch"})

        self.debug_build = debug_build

        self.config = {
            'name': name,
            'arch': arch,
            'arch_triplet': None,
            'template': None,
            'postmake': None,
            'prebuild': None,
            'build': None,
            'postbuild': None,
            'build_dir': '$ROOT/build/$ARCH_TRIPLET/$NAME',
            'src_dir': '$ROOT/libs/$NAME',
            'root_dir': root_dir,
            'dependencies_build': [],
            'dependencies_host': [],
            'dependencies_target': [],
            'dependencies_ppa': [],
            'make_jobs': 0,
            'docker_image': None,
            'build_args': [],
            'env_vars': {},
            'make_args': [],
            'install_dir': '$BUILD_DIR/install',
            'image_setup': {},
        }

        self.config.update(json_config)

        self.cleanup_config()

        self.config['arch_triplet'] = self.arch_triplet_mapping[self.config['arch']]

        for key in self.path_keys:
            if key not in self.accepts_placeholders and self.config[key]:
                self.config[key] = os.path.abspath(self.config[key])

        self.substitute_placeholders()
        self.set_env_vars()

        self.check_config_errors()

        for key, value in self.config.items():
            logger.debug('Lib {} config value {}: {}'.format(name, key, value))

    def __getattr__(self, name):
        return self.config[name]

    def __setattr__(self, name, value):
        if name in self.config:
            self.config[name] = value
        else:
            super().__setattr__(name, value)

    def prepare_docker_env_vars(self):
        docker_env_vars = []
        for key, val in self.get_env_vars().items():
            docker_env_vars.append('-e {}="{}"'.format(key, val))
        return " ".join(docker_env_vars)

    def set_env_vars(self):
        os.environ.update(self.get_env_vars())

    def get_env_vars(self):
        env_vars = {}

        if self.debug_build:
            env_vars['DEBUG_BUILD'] = '1'

        for key, conf in self.placeholders.items():
            env_vars[key] = self.config[conf]

        env_vars.update(self.config['env_vars'])

        return env_vars

    def substitute_placeholders(self):
        for key in self.accepts_placeholders:
            for sub in self.placeholders:
                substitute = "$"+sub
                rep = self.config[self.placeholders[sub]]
                if self.config[key]:
                    if isinstance(self.config[key], dict):
                        self.config[key] = {k: val.replace(substitute, rep) for (
                            k, val) in self.config[key].items()}
                    elif isinstance(self.config[key], list):
                        self.config[key] = [val.replace(
                            substitute, rep) for val in self.config[key]]
                    else:
                        self.config[key] = self.config[key].replace(
                            substitute, rep)
            if key in self.path_keys and self.config[key]:
                self.config[key] = os.path.abspath(self.config[key])

    def cleanup_config(self):
        self.make_args = merge_make_jobs_into_args(
            make_args=self.make_args, make_jobs=self.make_jobs)

        if self.config['dependencies_build']:
            self.config['dependencies_host'] += self.config['dependencies_build']
            self.config['dependencies_build'] = []
            logger.warning('"dependencies_build" is deprecated. Use "dependencies_host" instead!')

        for key in self.flexible_lists:
            self.config[key] = flexible_string_to_list(self.config[key])

        if self.config['docker_image']:
            self.custom_docker_image = True

    def check_config_errors(self):
        if self.config['template'] == self.CUSTOM and not self.config['build']:
            raise ClickableException(
                'When using the "custom" template you must specify a "build" in one the lib configs')

        if self.custom_docker_image:
            if self.dependencies_host or self.dependencies_target or self.dependencies_ppa:
                logger.warning(
                    "Dependencies are ignored when using a custom docker image!")
            if self.image_setup:
                logger.warning(
                    "Docker image setup is ignored when using a custom docker image!")
