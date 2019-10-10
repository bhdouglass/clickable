from clickable.logger import logger
from .query import Query


class Require(object):
    def __init__(self, query: Query):
        self.query = query

    def or_exit(self):
        if not self.query.is_met():
            self.print_instructions()
            logger.error('System requirement not met')
            exit(1)

    def print_instructions(self):
        instructions = self.query.get_user_instructions()
        if instructions is not None:
            logger.warning(instructions)
