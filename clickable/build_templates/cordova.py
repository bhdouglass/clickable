import subprocess
import shlex
import json
import shutil
import sys
import os
from distutils.dir_util import copy_tree

from .make import MakeBuilder
from clickable.utils import print_error, print_warning
from clickable.config import Config


class CordovaBuilder(MakeBuilder):
    name = Config.CORDOVA

    # Lots of this code was based off of this:
    # https://github.com/apache/cordova-ubuntu/blob/28cd3c1b53c1558baed4c66cb2deba597f05b3c6/bin/templates/project/cordova/lib/build.js#L59-L131
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.platform_dir = os.path.join(self.config.cwd, 'platforms/ubuntu/')
        self.sdk = 'ubuntu-sdk-16.04' if self.config.is_xenial else 'ubuntu-sdk-15.04'

        self._dirs = {
            'build': '{}/{}/{}/build/' .format(self.platform_dir, self.sdk, self.config.build_arch),
            'prefix': '{}/{}/{}/prefix/'.format(self.platform_dir, self.sdk, self.config.build_arch),
            'make': '{}/build'.format(self.platform_dir)
        }

        self.config.temp = self._dirs['build']
        self.config.dir = self._dirs['prefix']

        if not os.path.isdir(self.platform_dir):
            # fail when not using docker, need it anyways
            if self.config.container_mode or self.config.lxd:
                print_error('Docker is required to intialize cordova directories. Enable docker or run "cordova platform add ubuntu" manually to remove this message')
                sys.exit(1)

            command = 'cordova platform add ubuntu'

            # Can't use self.container.run_command because need to set -e HOME=/tmp
            wrapped_command = 'docker run -v {cwd}:{cwd} -w {cwd} -u {uid}:{uid} -e HOME=/tmp --rm -i {img} {cmd}'.format(
                cwd=self.config.cwd,
                uid=os.getuid(),
                img=self.base_docker_image,
                cmd=command
            )

            subprocess.check_call(shlex.split(wrapped_command))

    def clean_dir(self, path):
        if os.path.exists(path) and os.path.isdir(path):
            shutil.rmtree(path)

        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        except Exception:
            print_warning('Failed to create dir ({}): {}'.format(path, str(sys.exc_info()[0])))

    def build(self):
        self.clean_dir(self._dirs['build'])
        self.clean_dir(self._dirs['prefix'])
        self.container.run_command('cmake {} -DCMAKE_INSTALL_PREFIX={}'.format(self._dirs['make'], self._dirs['build']))

        super().build()

    def post_make(self):
        www_dir = os.path.join(self.platform_dir, 'www')
        shutil.rmtree(www_dir)
        shutil.copytree(os.path.join(self.config.cwd, 'www'), www_dir)
        shutil.copyfile(os.path.join(self.config.cwd, 'config.xml'), os.path.join(www_dir, 'config.xml'))

        copies = {
            'www': None,
            'platform_www': 'www',
            'config.xml': None,
            'cordova.desktop': None,
            'manifest.json': None,
            'apparmor.json': None,
        }

        # If value is none, set to key
        copies = {key: key if value is None else value
                  for key, value in copies.items()}

        # Is this overengineerd?
        for file_to_copy_source, file_to_copy_dest in copies.items():
            full_source_path = os.path.join(self.platform_dir,
                                            file_to_copy_source)
            full_dest_path = os.path.join(self._dirs['build'],
                                          file_to_copy_dest)
            if os.path.isdir(full_source_path):
                # https://stackoverflow.com/a/31039095/6381767
                copy_tree(full_source_path, full_dest_path)
            else:
                shutil.copy(full_source_path, full_dest_path)

        # Modify default files with updated settings
        # taken straing from cordova build.js
        manifest = self.config.get_manifest()
        manifest['architecture'] = self.config.build_arch
        manifest['framework'] = self.sdk
        with open(self.config.find_manifest(), 'w') as manifest_writer:
            json.dump(manifest, manifest_writer, indent=4)

        apparmor_file = os.path.join(self._dirs['build'], 'apparmor.json')
        with open(apparmor_file, 'r') as apparmor_reader:
            apparmor = json.load(apparmor_reader)
            apparmor['policy_version'] = 16.04 if self.config.is_xenial else 1.3

            if 'webview' not in apparmor['policy_groups']:
                apparmor['policy_groups'].append('webview')

            with open(apparmor_file, 'w') as apparmor_writer:
                json.dump(apparmor, apparmor_writer, indent=4)

        super().post_make()

    def make_install(self):
        # No DESTDIR needed
        self.container.run_command('make install')
