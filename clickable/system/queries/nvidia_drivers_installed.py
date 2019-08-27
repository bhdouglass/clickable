from clickable.system.access import is_program_installed
from clickable.system.query import Query


class NvidiaDriversInstalled(Query):
    def is_met(self):
        return is_program_installed('nvidia-smi')

    def get_user_instructions(self):
        return None
