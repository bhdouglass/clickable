import os
import glob
import shutil

from .base import Builder
from clickable.config import Config


class RustBuilder(Builder):
    name = Config.RUST

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paths_to_ignore = self._find_click_assets()
        self.paths_to_ignore.extend([
            # Click stuff
            os.path.abspath(self.config.install_dir),
            os.path.abspath(self.config.build_dir),
            'clickable.json',
            os.path.abspath(os.path.join(self.config.cwd, 'Cargo.toml')),
            os.path.abspath(os.path.join(self.config.cwd, 'Cargo.lock')),
            os.path.abspath(os.path.join(self.config.cwd, 'target')),
        ])
        self.paths_to_ignore.extend(self.config.ignore)

    @property
    def _cargo_target(self):
        if self.config.build_arch == 'armhf':
            return 'armv7-unknown-linux-gnueabihf'
        elif self.config.build_arch == 'amd64':
            return 'x86_64-unknown-linux-gnu'
        raise ValueError('Arch {} unsupported by rust template'.format(self.config.build_arch))

    def _find_click_assets(self):
        assets = glob.glob('{}/**/manifest.json'.format(self.config.cwd), recursive=True)
        assets.extend(glob.glob('{}/**/*.apparmor'.format(self.config.cwd), recursive=True))
        assets.extend(glob.glob('{}/**/*.desktop'.format(self.config.cwd), recursive=True))
        return assets

    def _ignore(self, path, contents):
        ignored = []
        for content in contents:
            abs_path = os.path.abspath(os.path.join(path, content))
            if (
                abs_path in self.paths_to_ignore or
                content in self.paths_to_ignore or
                os.path.splitext(content)[1] == '.rs'
            ):
                ignored += [content]
        return ignored

    def build(self):
        # Remove old artifacts unless the dirty option is active
        if not self.config.dirty and os.path.isdir(self.config.install_dir):
            shutil.rmtree(self.config.install_dir)

        # Copy project assets
        shutil.copytree(self.config.cwd, self.config.install_dir, ignore=self._ignore)

        # Copy click assets
        if self.config.build_arch == 'armhf':
            target_dir = self.config.install_dir + '/lib/arm-linux-gnueabihf/bin/'
        else:
            target_dir = self.config.install_dir
        os.makedirs(target_dir, exist_ok=True)
        assets = self._find_click_assets()
        for asset in assets:
            shutil.copy2(asset, self.config.install_dir)

        # Build using cargo
        cargo_command = 'cargo build {} --target {}' \
            .format('--release' if not self.config.debug_build else '',
                    self._cargo_target)
        self.config.container.run_command(cargo_command)

        # There could be more than one executable
        executables = glob.glob('{}/target/{}/{}/*'
                                .format(self.config.cwd,
                                        self._cargo_target,
                                        'debug' if self.config.debug_build else 'release'))
        for filename in filter(lambda f: os.path.isfile(f), executables):
            shutil.copy2(filename, '{}/{}'.format(
                target_dir,
                os.path.basename(filename)),
            )
