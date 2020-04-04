import subprocess
import shlex
import json
import shutil
import sys
import os
from distutils.dir_util import copy_tree

from .cmake import CMakeBuilder
from clickable.config.project import ProjectConfig
from clickable.config.constants import Constants


class CordovaBuilder(CMakeBuilder):
    name = Constants.CORDOVA

    # Lots of this code was based off of this:
    # https://github.com/apache/cordova-ubuntu/blob/28cd3c1b53c1558baed4c66cb2deba597f05b3c6/bin/templates/project/cordova/lib/build.js#L59-L131
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.platform_dir = os.path.join(self.config.cwd, 'platforms/ubuntu/')
        self.sdk = 'ubuntu-sdk-16.04'

        self.config.src_dir = os.path.join(self.platform_dir, 'build')

        if not os.path.isdir(self.platform_dir):
            command = self.config.container.run_command("cordova platform add ubuntu")

    def make_install(self):
        super().make_install()
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
            full_dest_path = os.path.join(self.config.install_dir,
                                          file_to_copy_dest)
            if os.path.isdir(full_source_path):
                # https://stackoverflow.com/a/31039095/6381767
                copy_tree(full_source_path, full_dest_path)
            else:
                shutil.copy(full_source_path, full_dest_path)

        # Modify default files with updated settings
        # taken straing from cordova build.js
        manifest = self.config.install_files.get_manifest()
        manifest['architecture'] = self.config.build_arch
        manifest['framework'] = self.sdk
        self.config.install_files.write_manifest(manifest)

        apparmor_file = os.path.join(self.config.install_dir, 'apparmor.json')
        with open(apparmor_file, 'r') as apparmor_reader:
            apparmor = json.load(apparmor_reader)
            apparmor['policy_version'] = 16.04

            if 'webview' not in apparmor['policy_groups']:
                apparmor['policy_groups'].append('webview')

            with open(apparmor_file, 'w') as apparmor_writer:
                json.dump(apparmor, apparmor_writer, indent=4)
