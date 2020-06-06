import os
import glob
import json
import xml.etree.ElementTree as ElementTree

from clickable.exceptions import ClickableException
from .constants import Constants
from ..utils import (
    find
)

class ProjectFiles(object):
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.desktop = None

    def find_any_desktop(self, temp_dir=None, build_dir=None):
        if self.desktop is not None:
            return self.desktop

        self.desktop = {}

        desktop_file = find(['.desktop', '.desktop.in', '.desktop.in.in'],
                self.project_dir, temp_dir, build_dir, extensions_only=True, depth=3)

        if desktop_file:
            with open(desktop_file, 'r') as f:
                # Not using configparser here since it has issues with %U that many apps have
                for line in f.readlines():
                    if '=' in line:
                        pos = line.find('=')
                        self.desktop[line[:pos]] = line[(pos + 1):].strip()

        return self.desktop

    def find_any_exec_line(self):
        desktop = self.find_any_desktop()

        exec_line = None
        if desktop and "Exec" in desktop:
            exec_line = desktop["Exec"]

        return exec_line

    def find_any_executable(self):
        exec_line = self.find_any_exec_line()

        executable = None
        if exec_line:
            exec_list = exec_line.split()

            for arg in exec_list:
                if "=" not in arg:
                    executable = arg
                    break

        return executable

    def find_any_exec_args(self, remove_proc_U=True):
        exec_line = self.find_any_exec_line()
        executable = self.find_any_executable()

        exec_args = None
        if exec_line and executable:
            exec_list = exec_line.split()
            pos = exec_list.index(executable)
            exec_args = exec_list[pos+1:]

            if '%U' in exec_args and remove_proc_U:
                exec_args.remove('%U')

            return exec_args

class InstallFiles(object):
    def __init__(self, install_dir, builder, arch):
        self.install_dir = install_dir
        self.builder = builder
        self.arch = arch

    def find_version(self):
        if self.builder == Constants.CORDOVA:
            tree = ElementTree.parse('config.xml')
            root = tree.getroot()
            version = root.attrib['version'] if 'version' in root.attrib else '1.0.0'
        else:
            version = self.get_manifest().get('version', '1.0')

        return version

    def find_package_name(self):
        if self.builder == Constants.CORDOVA:
            tree = ElementTree.parse('config.xml')
            root = tree.getroot()
            package = root.attrib['id'] if 'id' in root.attrib else None

            if not package:
                raise ClickableException('No package name specified in config.xml')

        else:
            package = self.get_manifest().get('name', None)

            if not package:
                raise ClickableException('No package name specified in manifest.json or clickable.json')

        return package

    def find_package_title(self):
        if self.builder == Constants.CORDOVA:
            tree = ElementTree.parse('config.xml')
            root = tree.getroot()
            title = root.attrib['name'] if 'name' in root.attrib else None

            if not title:
                raise ClickableException('No package title specified in config.xml')

        else:
            title = self.get_manifest().get('title', None)

            if not title:
                raise ClickableException(
                    'No package title specified in manifest.json or clickable.json')

        return title

    def find_app_name(self):
        app = None
        hooks = self.get_manifest().get('hooks', {})
        for key, value in hooks.items():
            if 'desktop' in value:
                app = key
                break

        if not app:  # If we don't find an app with a desktop file just find the first one
            apps = list(hooks.keys())
            if len(apps) > 0:
                app = apps[0]

        if not app:
            raise ClickableException('No app name specified in manifest.json')

        return app

    def find_full_package_name(self):
        return '{}_{}_{}'.format(
                self.find_package_name(),
                self.find_app_name(),
                self.find_version())

    def get_click_filename(self):
        return '{}_{}_{}.click'.format(self.find_package_name(), self.find_version(), self.arch)

    def write_manifest(self, manifest):
        with open(os.path.join(self.install_dir, "manifest.json"), 'w') as writer:
            json.dump(manifest, writer, indent=4)


    def load_manifest(self, manifest_path):
        manifest = {}
        with open(manifest_path, 'r') as f:
            try:
                manifest = json.load(f)
            except ValueError:
                raise ClickableException(
                    'Failed reading "manifest.json", it is not valid json')

        return manifest

    def get_manifest(self):
        return self.load_manifest(os.path.join(self.install_dir, "manifest.json"))

    def try_find_locale(self):
        return ':'.join(glob.glob("{}/**/locale".format(self.install_dir), recursive=True))

    def get_desktop(self, cwd, temp_dir=None, build_dir=None):
        desktop = {}

        desktop_file = find(['.desktop', '.desktop.in'], cwd, temp_dir, build_dir, extensions_only=True, depth=3)

        if desktop_file:
            with open(desktop_file, 'r') as f:
                # Not using configparser here since it has issues with %U that many apps have
                for line in f.readlines():
                    if '=' in line:
                        pos = line.find('=')
                        desktop[line[:pos]] = line[(pos + 1):].strip()

        return desktop
