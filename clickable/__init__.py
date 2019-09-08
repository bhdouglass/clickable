#!/usr/bin/env python3

import argparse
import sys
import inspect
import glob
from os.path import dirname, basename, isfile, join
import subprocess

from clickable.commands.base import Command
from clickable.config import Config
from clickable.container import Container
from clickable.utils import print_error


__version__ = '6.0.3'


class Clickable(object):
    def __init__(self):
        self.config = None
        self.command_classes = {}
        self.command_names = []
        self.command_aliases = {}
        self.command_help = {}

        command_dir = dirname(__file__)
        modules = glob.glob(join(command_dir, 'commands/*.py'))
        command_modules = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

        for name in command_modules:
            command_submodule = __import__('clickable.commands.{}'.format(name), globals(), locals(), [name])
            for name, cls in inspect.getmembers(command_submodule):
                if inspect.isclass(cls) and issubclass(cls, Command) and cls != Command and cls.name not in self.command_classes:
                    self.command_classes[cls.name] = cls
                    self.command_names.append(cls.name)
                    if cls.help:
                        self.command_help[cls.name] = cls.help

                    for alias in cls.aliases:
                        self.command_aliases[alias] = cls.name

    def show_valid_commands(self):
        n = [
            'Valid commands:',
            ', '.join(sorted(self.command_names))
        ]
        if self.config and hasattr(self.config, 'scripts') and self.config.scripts:
            n += [
                'Project-specific custom commands:',
                ', '.join(sorted(self.config.scripts.keys()))
            ]
        return '\n'.join(n)

    def print_valid_commands(self):
        print(self.show_valid_commands())

    def parse_args(self):
        parser = argparse.ArgumentParser(description='clickable')
        parser.add_argument('--version', '-v', action='version',
                            version='%(prog)s ' + __version__)
        parser.add_argument('commands', nargs='*', help=self.show_valid_commands())
        parser.add_argument(
            '--serial-number',
            '-s',
            help='Directs command to the device or emulator with the given serial number or qualifier (using adb)',
            default=None
        )
        parser.add_argument(
            '--config',
            '-c',
            help='Use specified config file instead of looking for the optional "clickable.json" in the current directory',
            default=None
        )
        parser.add_argument(
            '--ssh',
            help='Directs command to the device with the given IP address (using ssh)',
            default=None
        )
        parser.add_argument(
            '--arch',
            '-a',
            help='Use the specified arch when building (ignores the setting in clickable.json)'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Runs clickable in debug mode',
            default=False,
        )
        parser.add_argument(
            '--output',
            help='Where to output the compiled click package',
        )
        parser.add_argument(
            '--container-mode',
            action='store_true',
            help='Run all build commands on the current machine and not a container',
            default=False,
        )
        parser.add_argument(
            '--nvidia',
            action='store_true',
            help='Use docker with --runtime=nvidia and *-nvidia docker image',
            default=False,
        )
        parser.add_argument(
            '--apikey',
            help='Api key for the OpenStore',
        )
        parser.add_argument(
            '--docker-image',
            help='Use a specific docker image to build with'
        )
        parser.add_argument(
            '--dirty',
            action='store_true',
            help='Do not clean build directory',
            default=False,
        )
        parser.add_argument(
            '--debug-build',
            action='store_true',
            help='Perform a debug build',
            default=False,
        )
        parser.add_argument(
            '--gdbserver',
            help='Start gdbserver at the given port to debug the app remotely (only desktop mode)',
        )
        parser.add_argument(
            '--gdb',
            action='store_true',
            help='Start gdb to debug the app (only desktop mode)',
            default=False,
        )
        parser.add_argument(
            '--dark-mode',
            action='store_true',
            help='Use the dark theme when running apps (only desktop mode)',
            default=False,
        )

        args = parser.parse_args()
        if 'help' in args.commands:
            parser.print_help()
            sys.exit(0)

        return args

    def run(self, commands=[], args=None):
        self.config = Config(
            args=args,
            clickable_version=__version__,
            desktop=('desktop' in commands or 'test' in commands),
        )
        self.config.container = Container(self.config)

        VALID_COMMANDS = self.command_names + list(self.config.scripts.keys())

        if len(commands) == 0:
            commands = self.config.default.split(' ')

        '''
        Detect senarios when an argument is passed to a command. For example:
        `clickable install /path/to/click`. Since clickable allows commands
        to be strung together it makes detecting this harder. This check has
        been limited to just the case when we have 2 values in args.commands as
        stringing together multiple commands and a command with an argument is
        unlikely to occur.
        TODO determine if there is a better way to do this.
        '''
        command_arg = ''
        if len(commands) == 2 and commands[1] not in VALID_COMMANDS:
            command_arg = commands[1]
            commands = commands[:1]

        commands = [self.command_aliases[command] if command in self.command_aliases else command for command in commands]

        for command in commands:
            if command in self.command_names:
                cmd = self.command_classes[command](self.config)
                cmd.preprocess(command_arg)

        # TODO consider removing the ability to string together multiple commands
        # This should help clean up the arguments & command_arg
        for command in commands:
            if command in self.config.scripts:
                subprocess.check_call(self.config.scripts[command], cwd=self.config.cwd, shell=True)
            elif command in self.command_names:
                cmd = self.command_classes[command](self.config)
                cmd.run(command_arg)
            else:
                print_error('There is no builtin or custom command named "{}"'.format(command))
                self.print_valid_commands()
                sys.exit(1)


def main():
    clickable = Clickable()
    args = clickable.parse_args()

    try:
        clickable.run(args.commands, args)
    except Exception:
        if args.debug:
            raise
        else:
            print_error(str(sys.exc_info()[1]))
            sys.exit(1)


if __name__ == '__main__':
    main()
