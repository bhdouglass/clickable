from clickable import ProjectConfig
from clickable.commands.docker.docker_config import DockerConfig
from .docker_support import DockerSupport


class DebugGdbSupport(DockerSupport):
    config = None

    def __init__(self, config: ProjectConfig):
        self.config = config

    def update(self, docker_config: DockerConfig):
        if self.config.debug_gdb:
            if self.config.debug_gdb_port:
                port = self.config.debug_gdb_port
                docker_config.execute = 'gdbserver localhost:{} {}'.format(port, docker_config.execute)
                docker_config.add_extra_options({
                    '--publish': '{port}:{port}'.format(port=port)
                })
            else:
                docker_config.execute = 'gdb --args {}'.format(docker_config.execute)
                docker_config.add_extra_options({
                    '--cap-add': 'SYS_PTRACE',
                    '--security-opt seccomp': 'unconfined'
                })

