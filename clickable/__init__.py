#!/usr/bin/env python3

import argparse
import sys

from clickable.build_templates.cmake import CMakeClickable
from clickable.build_templates.cordova import CordovaClickable
from clickable.build_templates.custom import CustomClickable
from clickable.build_templates.go import GoClickable
from clickable.build_templates.pure import (
    PureQMLQMakeClickable,
    PureQMLCMakeClickable,
    PureClickable,
    PythonClickable,
)
from clickable.build_templates.qmake import QMakeClickable
from clickable.config import Config
from clickable.utils import print_error


__version__ = '4.4.1'


def main():
    config = None
    COMMAND_ALIASES = {
        'click_build': 'click_build',
        'build_click': 'click_build',
        'build-click': 'click_build',
        'writeable-image': 'writable_image',
    }

    COMMAND_HANDLERS = {
        'kill': 'kill',
        'clean': 'clean',
        'build': 'build',
        'click-build': 'click_build',
        'install': 'install',
        'launch': 'launch',
        'logs': 'logs',
        'setup-lxd': 'setup_lxd',
        'display-on': 'display_on',
        'no-lock': 'no_lock',
        'setup-docker': 'setup_docker',
        'update-docker': 'update_docker',
        'shell': 'shell',
        'devices': 'devices',
        'init': 'init_app',
        'run': 'run',
        'review': 'click_review',
        'writable-image': 'writable_image',
        'publish': 'publish',
    }

    def show_valid_commands():
        n = [
            'Valid commands:',
            ', '.join(sorted(COMMAND_HANDLERS.keys()))
        ]
        if config and hasattr(config, 'scripts') and config.scripts:
            n += [
                'Project-specific custom commands:',
                ', '.join(sorted(config.scripts.keys()))
            ]
        return '\n'.join(n)

    def print_valid_commands():
        print(show_valid_commands())

    parser = argparse.ArgumentParser(description='clickable')
    parser.add_argument('--version', '-v', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('commands', nargs='*', help=show_valid_commands())
    parser.add_argument(
        '--device',
        '-d',
        action='store_true',
        help='Whether or not to run the custom command on the device',
        default=False,
    )
    parser.add_argument(
        '--device-serial-number',
        '-s',
        help='Directs command to the device or emulator with the given serial number or qualifier (using adb)',
        default=None
    )
    parser.add_argument(
        '--ip',
        '-i',
        help='Directs command to the device with the given IP address (using ssh)'
    )
    parser.add_argument(
        '--arch',
        '-a',
        help='Use the specified arch when building (ignores the setting in clickable.json)'
    )
    parser.add_argument(
        '--template',
        '-t',
        help='Use the specified template when building (ignores the setting in clickable.json)'
    )

    # TODO depricate
    parser.add_argument(
        '--click',
        '-c',
        help='Installs the specified click (use with the "install" command)'
    )

    # TODO depricate
    parser.add_argument(
        '--app',
        '-p',
        help='Launches the specified app (use with the "launch" command)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Runs in debug mode',
        default=False,
    )
    parser.add_argument(
        '--lxd',
        action='store_true',
        help='Run build commands in a lxd container',
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
        '--name',
        '-n',
        help='Specify an app template name to use when running "clickable init"'
    )
    parser.add_argument(
        '--desktop',
        '-e',
        action='store_true',
        help='Run the app on the current machine for testing',
        default=False,
    )
    parser.add_argument(
        '--sdk',
        '-k',
        help='Use a specific version of the ubuntu sdk to compile against',
    )
    parser.add_argument(
        '--nvidia',
        action='store_true',
        help='Use nvidia-docker rather than docker',
        default=False,
    )
    parser.add_argument(
        '--apikey',
        help='Api key for the OpenStore',
    )
    parser.add_argument(
        '--xenial',
        action='store_true',
        help='Shortcut for --sdk=16.04',
        default=False,
    )

    args = parser.parse_args()

    skip_detection = False
    if args.click:
        skip_detection = True

    if len(args.commands) == 1:
        skip_commands = [
            'setup-lxd',
            'setup-docker',
            'shell',
            'no-lock',
            'display-on',
            'devices',
            'init',
        ]

        if args.commands[0] in skip_commands:
            skip_detection = True

    try:
        # TODO clean this up
        config = Config(
            ip=args.ip,
            arch=args.arch,
            template=args.template,
            skip_detection=skip_detection,
            lxd=args.lxd,
            click_output=args.output,
            container_mode=args.container_mode,
            desktop=args.desktop,
            sdk='16.04' if args.xenial else args.sdk,
            use_nvidia=args.nvidia,
            apikey=args.apikey,
        )

        VALID_COMMANDS = list(COMMAND_HANDLERS.keys()) + list(config.scripts.keys())

        clickable = None
        if config.template == config.PURE_QML_QMAKE:
            clickable = PureQMLQMakeClickable(config, args.device_serial_number)
        elif config.template == config.QMAKE:
            clickable = QMakeClickable(config, args.device_serial_number)
        elif config.template == config.PURE_QML_CMAKE:
            clickable = PureQMLCMakeClickable(config, args.device_serial_number)
        elif config.template == config.CMAKE:
            clickable = CMakeClickable(config, args.device_serial_number)
        elif config.template == config.CUSTOM:
            clickable = CustomClickable(config, args.device_serial_number)
        elif config.template == config.CORDOVA:
            clickable = CordovaClickable(config, args.device_serial_number)
        elif config.template == config.PURE:
            clickable = PureClickable(config, args.device_serial_number)
        elif config.template == config.PYTHON:
            clickable = PythonClickable(config, args.device_serial_number)
        elif config.template == config.GO:
            clickable = GoClickable(config, args.device_serial_number)

        commands = args.commands
        if len(args.commands) == 0:
            commands = config.default.split(' ')

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

        # TODO consider removing the ability to string together multiple commands
        # This should help clean up the arguments & new command_arg
        for command in commands:
            if command in config.scripts:
                clickable.script(command, args.device)
            elif command == 'install':
                clickable.install(args.click if args.click else command_arg)
            elif command == 'review':
                clickable.click_review(args.click if args.click else command_arg)
            elif command == 'launch':
                clickable.launch(args.app if args.app else command_arg)
            elif command == 'init':
                clickable.init_app(args.name)
            elif command == 'run':
                if not command_arg:
                    raise ValueError('No command supplied for `clickable run`')

                clickable.run(command_arg)
            elif command in COMMAND_HANDLERS:
                getattr(clickable, COMMAND_HANDLERS[command])()
            elif command in COMMAND_ALIASES:
                getattr(clickable, COMMAND_ALIASES[command])()
            elif command == 'help':
                parser.print_help()
            else:
                print_error('There is no builtin or custom command named "{}"'.format(command))
                print_valid_commands()
    except Exception:
        if args.debug:
            raise
        else:
            print_error(str(sys.exc_info()[1]))
            sys.exit(1)


if __name__ == '__main__':
    main()
