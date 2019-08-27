import re

from clickable.system.query import Query
from clickable.utils import run_subprocess_check_output


class LegacyDockerVersion(Query):
    EARLIEST_NON_LEGACY_VERSION = '19.03'

    def is_met(self):
        return self.is_version_older_than(
            expected=self.parse_version(self.EARLIEST_NON_LEGACY_VERSION),
            actual=self.parse_version(self.get_docker_version_string())
        )

    def is_legacy_docker_version(self, docker_version_string):
        return self.is_version_older_than(
            expected=self.parse_version('19.03'),
            actual=self.parse_version(docker_version_string)
        )

    def is_version_older_than(self, expected, actual):
        if actual['major'] == expected['major']:
            return actual['minor'] < expected['minor']

        return actual['major'] < expected['major']

    def parse_version(self, version_string):
        match = re.match(r'^(?P<major>\d+)\.(?P<minor>\d+)', version_string)
        return {
            'major': int(match.group('major')),
            'minor': int(match.group('minor'))
        }

    def get_docker_version_string(self):
        return run_subprocess_check_output("docker version --format '{{.Client.Version}}'")

    def get_user_instructions(self):
        return None
