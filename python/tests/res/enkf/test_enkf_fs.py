import os
import pytest

from tests import ResTest, tmpdir
from res.test import ErtTestContext

from res.enkf import EnkfFs
from res.enkf import EnKFMain
from res.enkf.enums import EnKFFSType


@pytest.mark.equinor_test
class EnKFFSTest(ResTest):
    def setUp(self):
        self.mount_point = "storage/default"
        self.config_file = self.createTestPath("Equinor/config/with_data/config")


    def test_id_enum(self):
        res_helper.assert_enum_fully_defined(EnKFFSType, "fs_driver_impl", "lib/include/ert/enkf/fs_types.hpp")

    @tmpdir(equinor="config/with_data/config")
    def test_create(self):
        assert EnkfFs.exists(self.mount_point)
        fs = EnkfFs(self.mount_point)
        assert 1 == fs.refCount()
        fs.umount()

        assert not EnkfFs.exists("newFS")
        arg = None
        fs = EnkfFs.createFileSystem("newFS", EnKFFSType.BLOCK_FS_DRIVER_ID, arg)
        assert EnkfFs.exists("newFS")
        assert  fs is None 

        with pytest.raises(IOError):
            version = EnkfFs.diskVersion("does/not/exist")

        version = EnkfFs.diskVersion("newFS")
        assert  version >= 106 

    @tmpdir(equinor="config/with_data/config")
    def test_create2(self):
        new_fs = EnkfFs.createFileSystem("newFS", EnKFFSType.BLOCK_FS_DRIVER_ID, mount = True)
        assert  isinstance( new_fs , EnkfFs )

    def test_throws(self):
        with pytest.raises(Exception):
            fs = EnkfFs("/does/not/exist")

