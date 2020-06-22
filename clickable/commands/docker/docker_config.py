import shlex
class DockerConfig(object):
    docker_executable = 'docker'
    volumes = {}
    environment = {}
    extra_options = {}
    extra_flags = []

    execute = None
    pseudo_tty = False

    working_directory = ''
    docker_image = ''

    uid = ''

    use_nvidia = False

    def add_volume_mappings(self, volume_mapping_dict):
        self.volumes.update(volume_mapping_dict)

    def add_environment_variables(self, environment_variables_dict):
        self.environment.update(environment_variables_dict)

    def add_extra_flags(self, extra_flags_list):
        self.extra_flags += extra_flags_list

    def add_extra_options(self, extra_options_dict):
        self.extra_options.update(extra_options_dict)

    def render_command(self):
        volume_mapping_string = self.render_volume_mapping_string()
        environment_string = self.render_environment_string()
        extra_options_string = self.render_extra_options_string()
        extra_flags_string = self.render_extra_flags_string()

        return self.render_command_string(
            volume_mapping_string,
            environment_string,
            extra_options_string,
            extra_flags_string,
        )

    def render_volume_mapping_string(self):
        # e.g. "-v /host/path:/container/path:Z -v /other/path:/other/path:Z
        return self.render_dictionary_as_mapping(self.volumes, '-v ', ':Z')

    def render_dictionary_as_mapping(self, dict, prefix='', suffix=''):
        return ' '.join(self.join_dictionary_items(dict, ':', prefix, suffix))

    def render_environment_string(self):
        # e.g. "-e VAR=value -e X=y
        return self.render_dictionary_as_variables(self.environment, '-e ')

    def render_dictionary_as_variables(self, dict, prefix=''):
        return ' '.join(self.join_dictionary_items(dict, '=', prefix))

    def join_dictionary_items(self, dict, glue=':', prefix='', suffix=''):
        return map(lambda key_value_list: '{prefix}{name}{glue}{value}{suffix}'.format(
            prefix=prefix,
            name=key_value_list[0],
            glue=glue,
            value=shlex.quote(key_value_list[1]),
            suffix=suffix
        ), dict.items())

    def render_extra_options_string(self):
        # {'--my-option': 'value', '--my-other-option': 'test'}
        # --my-option=value --my-other-option=test
        return self.render_dictionary_as_variables(self.extra_options)

    def render_extra_flags_string(self):
        # ['--my-flag', '--my-other-flag']
        # --my-flag --my-other-flag
        return ' '.join(self.extra_flags)

    def render_command_string(self, volumes_string, environment_string,
            extra_options_string, extra_flags_string):
        return (
            '{docker} run --privileged --net=host {volumes} {env} {extra_options} '
            '{extra_flags} -w {working_dir} --user={uid} '
            '--rm {tty} -i {docker_image} bash -c "{executable}"'
        ).format(
            docker=self.docker_executable,
            volumes=volumes_string,
            env=environment_string,
            extra_options=extra_options_string,
            extra_flags=extra_flags_string,
            working_dir=self.working_directory,
            uid=self.uid,
            docker_image=self.docker_image,
            executable=self.execute,
            tty="--tty" if self.pseudo_tty else ""
        )
