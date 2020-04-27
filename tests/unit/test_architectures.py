from clickable import Clickable
from .base_test import UnitTest

class TestArchitectures(UnitTest):
    def run_arch_test(self,
                      arch=None,
                      arch_agnostic_builder=False,
                      build_cmd=True,
                      restrict_arch_env=None,
                      restrict_arch=None,
                      expect_exception=False):
        config_env = {}
        if restrict_arch_env:
            config_env['CLICKABLE_ARCH'] = restrict_arch_env

        config_json = {}
        if arch_agnostic_builder:
            config_json["builder"] = "pure"
        else:
            config_json["builder"] = "cmake"
        if restrict_arch:
            config_json["restrict_arch"] = restrict_arch

        cli_args = []
        if arch:
            cli_args += ["--arch", arch]

        parser = Clickable.create_parser("Unit Test Call")
        run_args = parser.parse_args(cli_args)

        commands = ['no_command']
        if build_cmd:
            commands.append('build')

        self.setUpConfig(
            expect_exception = expect_exception,
            mock_config_json = config_json,
            mock_config_env = config_env,
            args = run_args,
            commands = commands,
        )

        if arch:
            expected_arch = arch
        elif restrict_arch:
            expected_arch = restrict_arch
        elif arch_agnostic_builder:
            expected_arch = "all"
        elif restrict_arch_env:
            expected_arch = restrict_arch_env
        else:
            expected_arch = "armhf"

        if not expect_exception:
            self.assertEqual(expected_arch, self.config.arch)

    def test_arch(self):
        self.run_arch_test('all')
        self.run_arch_test('amd64')
        self.run_arch_test('arm64')
        self.run_arch_test('armhf')
        self.run_arch_test(arch=None)

    def test_default_arch(self):
        self.run_arch_test(arch=None)
        self.run_arch_test(arch=None, restrict_arch_env='arm64')
        self.run_arch_test(arch=None, restrict_arch_env='arm64')
        self.run_arch_test(arch=None, restrict_arch_env='arm64',
                arch_agnostic_builder=True)
        self.run_arch_test(arch=None, restrict_arch_env='arm64',
                restrict_arch='all')
        self.run_arch_test(arch='all', restrict_arch_env='arm64')

    def test_arch_agnostic(self):
        self.run_arch_test('all', arch_agnostic_builder=True)
        self.run_arch_test(arch=None, arch_agnostic_builder=True)

    def test_fail_arch_agnostic(self):
        self.run_arch_test('armhf', arch_agnostic_builder=True,
                expect_exception=True)
        self.run_arch_test('armhf', arch_agnostic_builder=True,
                build_cmd=False, expect_exception=True)

    def test_restricted_arch_env(self):
        self.run_arch_test('all', restrict_arch_env='armhf')
        self.run_arch_test(arch=None, arch_agnostic_builder=True,
                restrict_arch_env='arm64')
        self.run_arch_test('amd64', restrict_arch_env='armhf', build_cmd=False)
        self.run_arch_test('arm64', restrict_arch_env='armhf', build_cmd=False)
        self.run_arch_test('armhf', restrict_arch_env='arm64', build_cmd=False)

    def test_fail_in_restricted_arch_env(self):
        self.run_arch_test('amd64', restrict_arch_env='armhf',
                expect_exception=True)
        self.run_arch_test('amd64', restrict_arch_env='all',
                expect_exception=True)

    def test_restricted_arch(self):
        self.run_arch_test('all', restrict_arch='all')
        self.run_arch_test('amd64', restrict_arch='amd64')

    def test_fail_in_restricted_arch(self):
        self.run_arch_test('amd64', restrict_arch='armhf',
                expect_exception=True)
        self.run_arch_test('amd64', restrict_arch='armhf', build_cmd=False,
                expect_exception=True)
        self.run_arch_test('all', restrict_arch='arm64', build_cmd=False,
                expect_exception=True)
        self.run_arch_test('arm64', restrict_arch='all', build_cmd=False,
                expect_exception=True)
