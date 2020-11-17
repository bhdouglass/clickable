#!/usr/bin/env python3

import argparse
import sys
import inspect
import glob
from os.path import dirname, basename, isfile, join
import subprocess
import logging

from clickable.commands.base import Command
from clickable.config.project import ProjectConfig
from clickable.container import Container
from clickable.logger import logger, log_file, console_handler
from clickable.exceptions import ClickableException


__version__ = '6.20.1'
__container_minimum_required__ = 2


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

    @staticmethod
    def create_parser(help_msg):
        parser = argparse.ArgumentParser(description='clickable')
        parser.add_argument('--version', '-v', action='version',
                            version='%(prog)s ' + __version__)
        parser.add_argument('commands', nargs='*', help=help_msg)
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
            help='Use the specified arch when building'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Allows to debug clickable by enabling verbose output',
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
            help='Do not clean build directory (affects default command chain and desktop command)',
            default=False,
        )
        parser.add_argument(
            '--debug-build',
            action='store_true',
            help='Perform a debug build (deprecated, use --debug instead)',
            default=False,
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Perform a debug build',
            default=False,
        )
        parser.add_argument(
            '--nvidia',
            action='store_true',
            help='Use docker with --runtime=nvidia and *-nvidia docker image',
            default=False,
        )
        parser.add_argument(
            '--no-nvidia',
            action='store_true',
            help="Don't use docker with --runtime=nvidia and *-nvidia docker image (disables automatic nvidia detection)",
            default=False,
        )
        parser.add_argument(
            '--gdbserver',
            help='Start gdbserver at the given port to debug the app remotely (only desktop mode, for on-device-debugging use gdbserver sub-command instead)',
        )
        parser.add_argument(
            '--gdb',
            action='store_true',
            help='Start gdb to debug the app (only desktop mode, for on-device-debugging use gdb sub-command instead)',
            default=False,
        )
        parser.add_argument(
            '--valgrind',
            action='store_true',
            help='Start valgrind to debug the app (only desktop mode)',
            default=False,
        )
        parser.add_argument(
            '--dark-mode',
            action='store_true',
            help='Use the dark theme when running apps (only desktop mode)',
            default=False,
        )
        parser.add_argument(
            '--lang',
            help='Start app in with the given language code (only desktop mode)',
        )
        parser.add_argument(
            '--skip-build',
            action='store_true',
            help='Start app without building it first (only desktop mode)',
            default=False,
        )
        parser.add_argument(
            '--non-interactive',
            action='store_true',
            help='Do not show prompts for anything (meant for CIs and integration into other tools)',
            default=False,
        )
        parser.add_argument(
            '--skip-review',
            action='store_true',
            help='Do not review click package after build (useful for unconfined apps)',
            default=False,
        )
        return parser

    def parse_args(self):
        parser = Clickable.create_parser(self.show_valid_commands())
        args = parser.parse_args()
        if 'help' in args.commands:
            parser.print_help()
            sys.exit(0)

        return args

    def setup_config(self, args, commands):
        return ProjectConfig(
            args=args,
            clickable_version=__version__,
            commands=commands,
        )

    def run(self, arg_commands=[], args=None):
        self.config = self.setup_config(args, arg_commands)
        self.config.container = Container(self.config,
                minimum_version=__container_minimum_required__)
        commands = self.config.commands

        VALID_COMMANDS = self.command_names + list(self.config.scripts.keys())

        is_default = not arg_commands

        '''
        Detect senarios when an argument is passed to a command. For example:
        `clickable install /path/to/click`. Since clickable allows commands
        to be strung together it makes detecting this harder. This check has
        been limited to just the case when we have 2 values in args.commands as
        stringing together multiple commands and a command with an argument is
        unlikely to occur.
        TODO remove chaining and clean this up
        '''
        command_arg = ''
        if len(commands) == 2 and commands[1] not in VALID_COMMANDS:
            command_arg = commands[1]
            commands = commands[:1]

        commands = [self.command_aliases[command] if command in self.command_aliases else command for command in commands]
        if len(commands) > 1 and not is_default:
            logger.warning('Chaining multiple commands is deprecated and will be rejected in a future version of Clickable.')

        for command in commands:
            if command in self.command_names:
                cmd = self.command_classes[command](self.config)
                cmd.preprocess(command_arg)

        for command in commands:
            if command == 'bash-completion':
                cli_args = [
                    '--serial-number', '--config', '--ssh', '--arch',
                    '--verbose', '--container-mode', '--apikey',
                    '--docker-image', '--dirty', '--debug',
                ]
                print(' '.join(sorted(VALID_COMMANDS + cli_args)))
            elif command == 'bash-completion-desktop':
                cli_args = [
                    '--nvidia', '--no-nvidia' '--gdbserver', '--gdb',
                    '--dark-mode', '--lang', '--skip-build', '--dirty',
                    '--verbose', '--config',
                ]
                print(' '.join(sorted(cli_args)))
            elif command in self.config.scripts:
                logger.debug('Running the "{}" script'.format(command))
                subprocess.check_call(self.config.scripts[command], cwd=self.config.cwd, shell=True)
            elif command in self.command_names:
                logger.debug('Running the "{}" command'.format(command))
                cmd = self.command_classes[command](self.config)
                cmd.run(command_arg)
            else:
                logger.error('There is no builtin or custom command named "{}"'.format(command))
                self.print_valid_commands()
                sys.exit(1)


def main():
    clickable = Clickable()
    args = clickable.parse_args()

    if args.verbose:
        console_handler.setLevel(logging.DEBUG)
    logger.debug('Clickable v' + __version__)

    try:
        clickable.run(args.commands, args)
    except ClickableException as e:
        logger.error(str(e))
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        logger.debug('Command exited with an error:' + str(e.cmd), exc_info=e)
        logger.critical('Command exited with non-zero exit status {}, see above for details. This is most likely not a problem with Clickable.'.format(
            e.returncode,
        ))

        sys.exit(2)
    except KeyboardInterrupt as e:
        logger.info('') # Print an empty space at then end so the cli prompt is nicer
        sys.exit(0)
    except Exception as e:
        if isinstance(e, OSError) and '28' in str(e):
            logger.critical('No space left on device')
            sys.exit(2)
            return

        logger.debug('Encountered an unknown error', exc_info=e)
        if not args.verbose:
            logger.critical('Encountered an unknown error: ' + str(e))

        logger.critical('If you believe this is a bug, please file a report at https://gitlab.com/clickable/clickable/issues with the log file located at ' + log_file)
        sys.exit(3)


if __name__ == '__main__':
    main()
