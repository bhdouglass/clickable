import shutil


def is_program_installed(cmd):
    path = shutil.which(cmd)
    return path is not None
