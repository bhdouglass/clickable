from clickable.system.access import is_program_installed
from clickable.system.query import Query


class NvidiaDocker(Query):

    def is_met(self):
        return is_program_installed('nvidia-docker')

    def get_user_instructions(self):
        return ("You are running clickable in nvidia mode.\n"
                "Please install nvidia-docker version 1 (not version 2).\n"
                "See https://github.com/NVIDIA/nvidia-docker/wiki/Installation-(version-1.0).\n")
