from clickable.system.access import is_program_installed
from clickable.system.query import Query
from clickable.utils import run_subprocess_check_output

class NvidiaDriversInUse(Query):
    def is_met(self):
        if not is_program_installed('nvidia-smi'):
            return False

        modules = run_subprocess_check_output('lsmod').splitlines()
        for m in modules:
            if m.split(' ', 1)[0] == 'nvidia':
                return True

        return False

    def get_user_instructions(self):
        return None
