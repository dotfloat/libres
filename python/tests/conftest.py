from __future__ import print_function

import pytest
import unittest
import resource
import functools
import sys
import os

from ecl.util.test import SourceEnumerator

def source_root():
    path_list = os.path.dirname(os.path.abspath(__file__)).split("/")
    while len(path_list) > 0:
        git_path = os.path.join(os.sep, "/".join(path_list), ".git")
        if os.path.isdir(git_path):
            return os.path.join(os.sep, *path_list)
        path_list.pop()
    raise RuntimeError('Cannot find the source folder')


def has_equinor_test_data():
    return os.path.isdir(os.path.join(source_root(), "test-data", "Equinor"))


def pytest_runtest_setup(item):
    if item.get_closest_marker("equinor_test") and not has_equinor_test_data():
        pytest.skip("Test requires Equinor data")


class ResHelper(object):
    SOURCE_ROOT = source_root()

    @classmethod
    def assert_enum_fully_defined(cls, enum_class, enum_name, source_path):
        enum_values = SourceEnumerator.findEnumerators(enum_name, os.path.join(cls.SOURCE_ROOT , source_path))

        for identifier, value in enum_values:
            if identifier not in enum_class.__dict__:
                raise AssertionError("Enum does not have identifier: {}".format(identifier))

            class_value = enum_class.__dict__[identifier]
            if int(class_value) != value:
                raise AssertionError("Enum value for identifier: {} does not match: {} != {}".format(identifier, class_value, value))


@pytest.fixture
def res_helper():
    return ResHelper()


@pytest.fixture(autouse=True)
def env_save():
    environment_pre = [(key, val) for key, val in os.environ.items() if key != "PYTEST_CURRENT_TEST"]
    yield
    environment_post = [(key, val) for key, val in os.environ.items() if key != "PYTEST_CURRENT_TEST"]
    if set(environment_pre) != set(environment_post):
        raise EnvironmentError("Your environment has changed after that test, please reset")
