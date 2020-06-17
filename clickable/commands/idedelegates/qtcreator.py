import os
import tarfile

from clickable.logger import logger
from .idedelegate import IdeCommandDelegate

class QtCreatorDelegate(IdeCommandDelegate):
    clickable_dir = os.path.expanduser('~/.clickable')
    project_path = os.getcwd()
    template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'qtcreator')
    init_settings_path = os.path.join(template_path, 'QtProject.tar.xz')
    target_settings_path = os.path.join(clickable_dir,'QtProject')


    def override_command(self, path):
        #point qtcreator to a custom location to make sure instance share the same configuration
        #also add current project's dir to make qtcreator open directly the project
        p = self.project_path if os.path.exists(os.path.join(self.project_path,'clickable.json')) else ''
        return path.replace('qtcreator', 'qtcreator -settingspath {} {}'.format(self.clickable_dir, p))


    def before_run(self, docker_config):

        #if first qtcreator launch, install common settings
        if not os.path.isdir(self.target_settings_path):
            logger.info('copy initial qtcreator settings to {}'.format(self.clickable_dir))
            tar = tarfile.open(self.init_settings_path)
            tar.extractall(self.clickable_dir)
            tar.close()

        if self.is_cmake_project() and not os.path.isfile(os.path.join(self.project_path, 'CMakeLists.txt.user')):
            self.init_cmake_project(docker_config)



    def is_cmake_project(self):
        return os.path.isfile(os.path.join(self.project_path,'CMakeLists.txt'))

    #templates run/build generation for cmake project
    def init_cmake_project(self, docker_config):
        env_vars = docker_config.environment

        #don't do all that if exec line not found
        if "CLICK_EXEC" in env_vars:

            clickable_ld_library_path='{}:{}'.format(env_vars["LD_LIBRARY_PATH"], env_vars["CLICK_LD_LIBRARY_PATH"])
            clickable_qml2_import_path='{}:{}'.format(env_vars["QML2_IMPORT_PATH"], env_vars["CLICK_QML2_IMPORT_PATH"])

            template_replacement = {
                "CLICKABLE_LD_LIBRARY_PATH": clickable_ld_library_path,
                "CLICKABLE_QML2_IMPORT_PATH":clickable_qml2_import_path,
                "CLICKABLE_BUILD_DIR":env_vars["BUILD_DIR"],
                "CLICKABLE_INSTALL_DIR":env_vars["INSTALL_DIR"],
                "CLICKABLE_EXEC_CMD":env_vars["CLICK_EXEC"],
                "CLICKABLE_EXEC_ARGS":env_vars["CLICK_EXEC_PARAMS"]
            }

            #choose the right template according to the exec command
            template_file_name = 'CMakeLists.txt.user.shared.binary.in'

            if env_vars["CLICK_EXEC"] == 'qmlscene':
                template_file_name = 'CMakeLists.txt.user.shared.qmlscene.in'

            template_path = os.path.join(self.template_path,template_file_name)
            output_path = os.path.join(self.project_path,'CMakeLists.txt.user.shared')
            #now read template and generate the .shared file to the root project dir
            with open(template_path, "r") as infile2, open(output_path, "w") as outfile:
                for line in infile2:
                    for f_key, f_value in template_replacement.items():
                        if f_key in line:
                            line = line.replace(f_key, f_value)
                    outfile.write(line)

            logger.info('generated default build/run template to {}'.format(output_path))