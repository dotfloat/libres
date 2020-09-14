import os
from res.test import ErtTestContext
from tests import ResTest
from tests.utils import tmpdir

from res.enkf import EnkfFs
from res.enkf import EnKFMain
from res.enkf import EnkfFsManager



class EnKFFSManagerTest1(ResTest):
    def setUp(self):
        self.config_file = self.createTestPath("local/snake_oil/snake_oil.ert")

    @tmpdir()
    def test_create(self):
        # We are indirectly testing the create through the create
        # already in the enkf_main object. In principle we could
        # create a separate manager instance from the ground up, but
        # then the reference count will be weird.
        with ErtTestContext("enkf_fs_manager_create_test", self.config_file) as testContext:
            ert = testContext.getErt()
            fsm = ert.getEnkfFsManager()

            fs = fsm.getCurrentFileSystem()
            assert fsm.isCaseMounted("default_0")
            assert fsm.caseExists("default_0")
            assert fsm.caseHasData("default_0")
            assert not fsm.isCaseRunning("default_0")

            assert 1 == fsm.getFileSystemCount()

            assert not fsm.isCaseMounted("newFS")
            assert not fsm.caseExists("newFS")
            assert not fsm.caseHasData("newFS")
            assert not fsm.isCaseRunning("newFS")

            fs2 = fsm.getFileSystem("newFS")
            assert 2 == fsm.getFileSystemCount()

            assert fsm.isCaseMounted("newFS")
            assert fsm.caseExists("newFS")
            assert not fsm.caseHasData("newFS")
            assert not fsm.isCaseRunning("newFS")
