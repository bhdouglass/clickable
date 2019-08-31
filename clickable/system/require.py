from clickable.utils import print_warning, print_error
from .query import Query


class Require(object):
    def __init__(self, query: Query):
        self.query = query

    def or_exit(self):
        if not self.query.is_met():
            self.print_instructions()
            print_error('System requirement not met')
            exit(1)

    def print_instructions(self):
        instructions = self.query.get_user_instructions()
        if instructions is not None:
            print_warning(instructions)
