import sys
import os
from tests import ResTest
from res.test import ErtTestContext
from tests.utils import tmpdir


from res.enkf import EnkfFs
from res.enkf import EnKFMain
from res.enkf import EnkfFsManager


class EnKFFSManagerTest2(ResTest):
    def setUp(self):
        self.config_file = self.createTestPath("local/custom_kw/mini_config")

    @tmpdir()
    def test_rotate(self):

        # We are indirectly testing the create through the create
        # already in the enkf_main object. In principle we could
        # create a separate manager instance from the ground up, but
        # then the reference count will be weird.
        with ErtTestContext("enkf_fs_manager_rotate_test", self.config_file) as testContext:
            ert = testContext.getErt()
            fsm = ert.getEnkfFsManager()
            assert 0 == fsm.getFileSystemCount()

            fs_list = []
            for index in range(EnkfFsManager.DEFAULT_CAPACITY):
                fs_list.append(fsm.getFileSystem("fs_fill_%d" % index))

            for fs in fs_list:
                assert 2 == fs.refCount()
                fs_copy = fs.copy( )
                assert 3 == fs.refCount()
                assert 3 == fs_copy.refCount()

                del fs_copy
                assert 2 == fs.refCount()


            assert EnkfFsManager.DEFAULT_CAPACITY == fsm.getFileSystemCount()

            for i in range(3 * EnkfFsManager.DEFAULT_CAPACITY):
                fs_name = "fs_test_%d" % i
                sys.stderr.write("Mounting: %s\n" % fs_name)
                fs = fsm.getFileSystem(fs_name)
                assert EnkfFsManager.DEFAULT_CAPACITY == fsm.getFileSystemCount()
