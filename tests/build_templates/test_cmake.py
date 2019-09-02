from unittest import TestCase, mock
import os
import hashlib

from clickable import main


class TestCMakeBuilder(TestCase):
    def setUp(self):
        self.original_path = os.getcwd()
        self.path = os.path.join(os.path.dirname(__file__), 'apps/cmake-test/')
        os.chdir(self.path)

    def tearDown(self):
        os.chdir(self.original_path)

    def test_cmake(self):
        main()

        click = os.path.join(self.path, 'build/x86_64-linux-gnu/app/cmake-test.clickable_1.0.0_amd64.click')
        self.assertTrue(os.path.exists(click))
