import os
import tarfile
import re

from clickable.logger import logger, Colors
from .idedelegate import IdeCommandDelegate

class QtCreatorDelegate(IdeCommandDelegate):
    clickable_dir = os.path.expanduser('~/.clickable')
    project_path = os.getcwd()
    template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'qtcreator')
    init_settings_path = os.path.join(template_path, 'QtProject.tar.xz')
    target_settings_path = os.path.join(clickable_dir,'QtProject')
    template_path = os.path.join(template_path,'CMakeLists.txt.user.shared.in')


    def override_command(self, path):
        #point qtcreator to a custom location to make sure instance share the same configuration
        #also add current project's dir to make qtcreator open directly the project
        p = self.project_path if os.path.exists(os.path.join(self.project_path,'clickable.json')) else ''
        return path.replace('qtcreator', 'qtcreator -settingspath {} {}'.format(self.clickable_dir, p))


    def before_run(self, config, docker_config):

        #if first qtcreator launch, install common settings
        if not os.path.isdir(self.target_settings_path):
            logger.info('copy initial qtcreator settings to {}'.format(self.clickable_dir))
            tar = tarfile.open(self.init_settings_path)
            tar.extractall(self.clickable_dir)
            tar.close()

        if self.is_cmake_project() and not os.path.isfile(os.path.join(self.project_path, 'CMakeLists.txt.user')):
            self.init_cmake_project(config, docker_config)



    def is_cmake_project(self):
        return os.path.isfile(os.path.join(self.project_path,'CMakeLists.txt'))

    #templates run/build generation for cmake project
    def init_cmake_project(self, config, docker_config):

        executable = config.project_files.find_any_executable()
        exec_args = config.project_files.find_any_exec_args()
        #don't do all that if exec line not found
        if executable:

            choice = input(Colors.INFO + 'Do you want Clickable to setup a QtCreator project for you? [Y/n]: ' + Colors.CLEAR
                           ).strip().lower()
            if choice != 'y' and choice != 'yes' and choice != '':
                return

            #just check if CLICK_EXEC is a variable
            if re.match("@([-\w]+)@", executable):
                logger.warning("Could not determine executable command '{}', please adjust your project's run settings".format(executable))

            # work around for qtcreator bug when first run of a project to avoid qtcreator hang
            # we need to create the build directory first
            if not os.path.isdir(config.build_dir):
                os.makedirs(config.build_dir)

            env_vars = docker_config.environment
            clickable_ld_library_path='{}:{}'.format(env_vars["LD_LIBRARY_PATH"], env_vars["CLICK_LD_LIBRARY_PATH"])
            clickable_qml2_import_path='{}:{}'.format(env_vars["QML2_IMPORT_PATH"], env_vars["CLICK_QML2_IMPORT_PATH"])

            template_replacement = {
                "CLICKABLE_LD_LIBRARY_PATH": clickable_ld_library_path,
                "CLICKABLE_QML2_IMPORT_PATH": clickable_qml2_import_path,
                "CLICKABLE_BUILD_DIR": config.build_dir,
                "CLICKABLE_INSTALL_DIR": config.install_dir,
                "CLICKABLE_EXEC_CMD": executable,
                "CLICKABLE_EXEC_ARGS": " ".join(exec_args),
                "CLICKABLE_SRC_DIR": config.src_dir,
                "CLICKABLE_BUILD_ARGS": " ".join(config.build_args),
            }

            output_path = os.path.join(self.project_path,'CMakeLists.txt.user.shared')
            #now read template and generate the .shared file to the root project dir
            with open(self.template_path, "r") as infile2, open(output_path, "w") as outfile:
                for line in infile2:
                    for f_key, f_value in template_replacement.items():
                        if f_key in line:
                            line = line.replace(f_key, f_value)
                    outfile.write(line)

            logger.info('generated default build/run template to {}'.format(output_path))