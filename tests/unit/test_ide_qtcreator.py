import os
import shutil
from clickable.commands.ide import IdeCommand
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
                "CLICK_EXEC": "qmlscene",
                "CLICK_EXEC_PARAMS": "qml/Main.qml",
                "INSTALL_DIR": "/tmp/fake/qmlproject",
                "BUILD_DIR": "/tmp/fake/qmlproject/build/app",
                "LD_LIBRARY_PATH":"/usr/bin",
                "CLICK_LD_LIBRARY_PATH":"/tmp/fake/qmlproject/build/app/install",
                "QML2_IMPORT_PATH":"/tmp/qmllibs",
                "CLICK_QML2_IMPORT_PATH":"/tmp/fake/qmlproject/build/app/install"
            }
        )
        self.idedelegate = QtCreatorDelegate()
        self.idedelegate.clickable_dir = '/tmp/tests/.clickable'
        self.idedelegate.project_path = '/tmp/tests/qmlproject'
        self.idedelegate.target_settings_path = os.path.join(self.idedelegate.clickable_dir ,'QtProject')

        os.makedirs(self.idedelegate.project_path)


    def test_command_overrided(self):

        path_arg =  self.idedelegate.override_command('qtcreator')

        self.assertEqual(path_arg, 'qtcreator -settingspath {} {}'.format(self.idedelegate.clickable_dir, self.idedelegate.project_path))

    def test_initialize_qtcreator_conf(self):

        self.idedelegate.before_run(self.docker_config)
        self.assertTrue(os.path.isdir('/tmp/tests/.clickable/QtProject'))

    def test_init_cmake_project(self):

        output_file = os.path.join(self.idedelegate.project_path, 'CMakeLists.txt.user.shared')


        #if Exec not found in desktop, should do nothing
        self.docker_config.environment.pop('CLICK_EXEC', None)
        self.idedelegate.init_cmake_project(self.docker_config)
        self.assertFalse(os.path.isfile(output_file))

        #normal case
        self.docker_config.add_environment_variables(
            {
                "CLICK_EXEC": "qmlscene",
                "CLICK_EXEC_PARAMS": "qml/Main.qml",
            })

        self.idedelegate.init_cmake_project(self.docker_config)
        self.assertTrue(os.path.isfile(output_file))
        #test an example variable that have been replaced
        self.assertTrue(open(output_file, 'r').read().find('CustomExecutableRunConfiguration.Arguments">qmlscene</value>'))

    def tearDown(self):
        shutil.rmtree(self.idedelegate.project_path, ignore_errors=True)
