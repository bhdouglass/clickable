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
                "CLICK_QML2_IMPORT_PATH":"/tmp/fake/qmlproject/build/app/install",
                "CLICK_PATH":"/tmp/fake/qmlproject/build/app/install/lib"
            }
        )

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

    def test_recurse_replace(self):

        final_command = self.idedelegate.recurse_replace('qmlscene --ok=\"args\"', {})
        self.assertEquals('qmlscene --ok=\"args\"', final_command)

        final_command = self.idedelegate.recurse_replace('\"qmlscene --ok=\"args\"\"', {})
        self.assertEquals('\"qmlscene --ok=\"args\"\"', final_command)

        cmake_vars = {
            'FAKE':'qmlscene'
        }
        final_command = self.idedelegate.recurse_replace('${FAKE} --ok=\"args\"', cmake_vars)
        self.assertEquals('qmlscene --ok=\"args\"', final_command)

        #test with recursive vars
        cmake_vars = {
            'FAKE_SUBVAR':'share/foo',
            'FAKE_VAR':'${FAKE_SUBVAR}/hello'
        }
        final_command = self.idedelegate.recurse_replace('${FAKE_VAR} --args someargs', cmake_vars)
        self.assertEquals('share/foo/hello --args someargs', final_command)

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


    @mock.patch('clickable.config.file_helpers.ProjectFiles.find_any_executable', return_value='@FAKE_EXE@')
    @mock.patch('clickable.config.file_helpers.ProjectFiles.find_any_exec_args', return_value=[])
    def test_init_cmake_project_exe_as_var(self, find_any_executable_mock, find_any_exec_args_mock):
        #mock prompt
        original_input = mock.builtins.input
        mock.builtins.input = lambda _: "yes"

        #Exec command as variable
        cmake_file = open(os.path.join(self.idedelegate.project_path,'CMakeLists.txt'), 'w')
        cmake_file.write("set(FAKE_EXE \"qmlscene --ok=\"args\"\")")
        cmake_file.close()

        self.idedelegate.init_cmake_project(self.config, self.docker_config)
        #test that final exe var is found
        generated_shared_file = open(self.output_file, 'r').read()
        self.assertTrue(generated_shared_file.find('CustomExecutableRunConfiguration.Arguments">qmlscene</value>'))
        self.assertTrue(generated_shared_file.find('CustomExecutableRunConfiguration.Arguments">--ok="args"</value>'))


    def tearDown(self):
        shutil.rmtree(self.idedelegate.project_path, ignore_errors=True)
