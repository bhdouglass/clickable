import os
import shutil
from clickable.commands.docker.docker_config import DockerConfig
from clickable.commands.idedelegates.qtcreator import QtCreatorDelegate

from .base_test import UnitTest
from unittest import mock

class TestIdeQtCreatorCommand(UnitTest):

    def setUp(self):
        self.setUpConfig()
        self.docker_config = DockerConfig()
        self.docker_config.add_environment_variables(
            {
                "LD_LIBRARY_PATH":"/usr/bin",
                "CLICK_LD_LIBRARY_PATH":"/tmp/fake/qmlproject/build/app/install",
                "QML2_IMPORT_PATH":"/tmp/qmllibs",
                "CLICK_QML2_IMPORT_PATH":"/tmp/fake/qmlproject/build/app/install"
            }
        )

        # self.project_files = ProjectFiles('/tmp/fake/qmlproject')
        #
        # self.projectConfig = ProjectConfig()
        # self.config = {
        #     'src_dir': '/tmp/fake/qmlproject',
        #     'build_dir': '/tmp/fake/qmlproject/build/app',
        #     'build_args': [],
        #     'install_dir': '/tmp/fake/qmlproject/build/app/install',
        # }
        # print('OLLLALALAL' + self.config.src_dir)


        self.idedelegate = QtCreatorDelegate()
        self.idedelegate.clickable_dir = '/tmp/tests/.clickable'
        self.idedelegate.project_path = '/tmp/tests/qmlproject'
        self.output_file = os.path.join(self.idedelegate.project_path, 'CMakeLists.txt.user.shared')

        self.idedelegate.target_settings_path = os.path.join(self.idedelegate.clickable_dir ,'QtProject')

        os.makedirs(self.idedelegate.project_path)


    def test_command_overrided(self):

        #path should not be added to qtcreator command if no clickable.json found
        path_arg =  self.idedelegate.override_command('qtcreator')
        self.assertEqual(path_arg, 'qtcreator -settingspath {} '.format(self.idedelegate.clickable_dir))

        #create a fake clickable.json file, overrided path should now be with the current directory
        open(os.path.join(self.idedelegate.project_path,'clickable.json'), 'a')
        path_arg =  self.idedelegate.override_command('qtcreator')
        self.assertEqual(path_arg, 'qtcreator -settingspath {} {}'.format(self.idedelegate.clickable_dir, self.idedelegate.project_path))

    def test_initialize_qtcreator_conf(self):

        self.idedelegate.before_run(None, self.docker_config)
        self.assertTrue(os.path.isdir('/tmp/tests/.clickable/QtProject'))


    @mock.patch('clickable.config.file_helpers.ProjectFiles.find_any_executable', return_value='')
    @mock.patch('clickable.config.file_helpers.ProjectFiles.find_any_exec_args')
    def test_init_cmake_project_no_exe(self, find_any_executable_mock, find_any_exec_args_mock):

        #if Exec not found in desktop, should do nothing
        self.idedelegate.init_cmake_project(self.config, self.docker_config)
        self.assertFalse(os.path.isfile(self.output_file))

    @mock.patch('clickable.config.file_helpers.ProjectFiles.find_any_executable', return_value='fake_exe')
    @mock.patch('clickable.config.file_helpers.ProjectFiles.find_any_exec_args')
    def test_init_cmake_project_no_to_prompt(self, find_any_executable_mock, find_any_exec_args_mock):
        #mock prompt
        original_input = mock.builtins.input
        mock.builtins.input = lambda _: "no"

        #user choose not to let clickable generate config
        self.idedelegate.init_cmake_project(self.config, self.docker_config)
        self.assertFalse(os.path.isfile(self.output_file))


    @mock.patch('clickable.config.file_helpers.ProjectFiles.find_any_executable', return_value='fake_exe')
    @mock.patch('clickable.config.file_helpers.ProjectFiles.find_any_exec_args', return_value=[])
    def test_init_cmake_project(self, find_any_executable_mock, find_any_exec_args_mock):
        #mock prompt
        original_input = mock.builtins.input
        mock.builtins.input = lambda _: "yes"

        #now he is ok to let clickable build the configuration template
        self.idedelegate.init_cmake_project(self.config, self.docker_config)
        self.assertTrue(os.path.isfile(self.output_file))
        #test an example variable that have been replaced
        self.assertTrue(open(self.output_file, 'r').read().find('CustomExecutableRunConfiguration.Arguments">fake_exe</value>'))

        mock.builtins.input = original_input

    def tearDown(self):
        shutil.rmtree(self.idedelegate.project_path, ignore_errors=True)
