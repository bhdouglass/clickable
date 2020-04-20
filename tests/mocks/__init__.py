from .config import ConfigMock
from .clickable import ClickableMock


def empty_fn(*args, **kwargs):
    pass


def true_fn(*args, **kwargs):
    return True


def false_fn(*args, **kwargs):
    return False


def exception_fn(*args, **kwargs):
    raise Exception()
