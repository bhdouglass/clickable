from clickable.system.access import is_program_installed
from clickable.system.query import Query


class NvidiaModprobe(Query):

    def is_met(self):
        return is_program_installed('nvidia-modprobe')

    def get_user_instructions(self):
        return ("You are running clickable in nvidia mode.\n"
                "Please install nvidia-modprobe.\n")
