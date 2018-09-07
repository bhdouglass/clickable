import subprocess
import shlex
import json
import shutil
import sys
import os
import xml.etree.ElementTree as ElementTree
from distutils.dir_util import copy_tree

from .cmake import CMakeClickable
from clickable.utils import print_error, print_warning, find_manifest, get_manifest


class CordovaClickable(CMakeClickable):
    # Lots of this code was based off of this:
    # https://github.com/apache/cordova-ubuntu/blob/28cd3c1b53c1558baed4c66cb2deba597f05b3c6/bin/templates/project/cordova/lib/build.js#L59-L131
    def __init__(self, *args, **kwargs):
        super(CMakeClickable, self).__init__(*args, **kwargs)

        self.platform_dir = os.path.join(self.cwd, 'platforms/ubuntu/')

        self._dirs = {
            'build': '{}/{}/{}/build/' .format(self.platform_dir, self.config.sdk, self.build_arch),
            'prefix': '{}/{}/{}/prefix/'.format(self.platform_dir, self.config.sdk, self.build_arch),
            'make': '{}/build'.format(self.platform_dir)
        }

        self.temp = self._dirs['build']

        if not os.path.isdir(self.platform_dir):
            # fail when not using docker, need it anyways
            if self.config.container_mode or self.config.lxd:
                print_error('Docker is required to intialize cordova directories. Enable docker or run "cordova platform add ubuntu" manually to remove this message')
                sys.exit(1)

            cordova_docker_image = "beevelop/cordova:v7.0.0"  # TODO add cordova to the clickable image
            command = "cordova platform add ubuntu"

            # Can't use self.run_container_command because need to set -e HOME=/tmp
            wrapped_command = 'docker run -v {cwd}:{cwd} -w {cwd} -u {uid}:{uid} -e HOME=/tmp --rm -i {img} {cmd}'.format(
                cwd=self.cwd,
                uid=os.getuid(),
                img=cordova_docker_image,
                cmd=command
            )

            subprocess.check_call(shlex.split(wrapped_command))

        self.config.dir = self._dirs['prefix']

    def _build(self):

        # Clear out prefix directory
        # IK this is against DRY, but I copied this code from MakeClickable.make_install
        if os.path.exists(self.config.dir) and os.path.isdir(self.temp):
            shutil.rmtree(self.config.dir)

        try:
            os.makedirs(self.config.dir)
        except FileExistsError:
            print_warning('Failed to create temp dir, already exists')
        except Exception:
            print_warning('Failed to create temp dir ({}): {}'.format(self.temp, str(sys.exc_info()[0])))

        self.run_container_command('cmake {} -DCMAKE_INSTALL_PREFIX={}'.format(self._dirs['make'], self._dirs['build']))

        super(CMakeClickable, self)._build()

    def post_make(self):
        super(CordovaClickable, self).post_make()

        www_dir = os.path.join(self.platform_dir, "www")
        shutil.rmtree(www_dir)
        shutil.copytree(os.path.join(self.cwd, "www"), www_dir)
        shutil.copyfile(os.path.join(self.cwd, "config.xml"), os.path.join(www_dir, 'config.xml'))

        copies = {
            "www": None,
            "platform_www": "www",
            "config.xml": None,
            "cordova.desktop": None,
            "manifest.json": None,
            "apparmor.json": None,
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
        with open(self.find_manifest(), 'r') as manifest_reader:
            manifest = json.load(manifest_reader)
            manifest['architecture'] = self.build_arch
            manifest['framework'] = self.config.sdk
            with open(self.find_manifest(), 'w') as manifest_writer:
                json.dump(manifest, manifest_writer, indent=4)

        apparmor_file = os.path.join(self._dirs['build'], 'apparmor.json')
        with open(apparmor_file, 'r') as apparmor_reader:
            apparmor = json.load(apparmor_reader)
            apparmor["policy_version"] = 1.3

            if 'webview' not in apparmor["policy_groups"]:
                apparmor["policy_groups"].append("webview")

            with open(apparmor_file, 'w') as apparmor_writer:
                json.dump(apparmor, apparmor_writer, indent=4)

    def make_install(self):
        # This is beause I don't want a DESTDIR
        self.run_container_command('make install')

    def find_manifest(self):
        return find_manifest(self._dirs['build'])

    def get_manifest(self):
        return get_manifest(self._dirs['build'])

    def find_package_name(self):
        tree = ElementTree.parse('config.xml')
        root = tree.getroot()
        return root.attrib['id'] if 'id' in root.attrib else '1.0.0'

    def find_version(self):
        tree = ElementTree.parse('config.xml')
        root = tree.getroot()
        return root.attrib['version'] if 'version' in root.attrib else '1.0.0'
