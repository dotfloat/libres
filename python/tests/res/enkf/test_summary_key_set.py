import os
import pytest

from tests import ResTest, tmpdir
from res.test.ert_test_context import ErtTestContext

from res.enkf import SummaryKeySet
from res.enkf.enkf_fs import EnkfFs
from res.enkf import EnKFMain, ResConfig


@pytest.mark.equinor_test
class SummaryKeySetTest(ResTest):

    def test_creation(self):

        keys = SummaryKeySet()

        assert len(keys) == 0

        assert keys.addSummaryKey("FOPT")

        assert len(keys) == 1

        assert "FOPT" in keys

        assert set(["FOPT"]) == set(keys.keys())

        assert keys.addSummaryKey("WWCT")

        assert len(keys) == 2

        assert "WWCT" in keys

        assert set(["WWCT", "FOPT"]) == set(keys.keys())



    @tmpdir()
    def test_read_only_creation(self):
        keys = SummaryKeySet()

        keys.addSummaryKey("FOPT")
        keys.addSummaryKey("WWCT")

        filename = "test.txt"
        keys.writeToFile(filename)

        keys_from_file = SummaryKeySet(filename, read_only=True)
        assert set(keys.keys()) == set(keys_from_file.keys())

        assert keys_from_file.isReadOnly()
        assert not keys_from_file.addSummaryKey("WOPR")

    @tmpdir()
    def test_write_to_and_read_from_file(self):
        keys = SummaryKeySet()

        keys.addSummaryKey("FOPT")
        keys.addSummaryKey("WWCT")

        filename = "test.txt"

        assert not os.path.exists(filename)

        keys.writeToFile(filename)

        assert os.path.exists(filename)

        keys_from_file = SummaryKeySet(filename)
        assert set(keys.keys()) == set(keys_from_file.keys())

    @tmpdir(equinor="config/with_data")
    def test_with_enkf_fs(self):
        config_file = self.createTestPath("Equinor/config/with_data/config")

        fs = EnkfFs("storage/default")
        summary_key_set = fs.getSummaryKeySet()
        summary_key_set.addSummaryKey("FOPT")
        summary_key_set.addSummaryKey("WWCT")
        summary_key_set.addSummaryKey("WOPR")
        fs.umount()

        res_config = ResConfig("config")
        ert = EnKFMain(res_config)
        fs = ert.getEnkfFsManager().getCurrentFileSystem()
        summary_key_set = fs.getSummaryKeySet()
        assert "FOPT" in summary_key_set
        assert "WWCT" in summary_key_set
        assert "WOPR" in summary_key_set

        ensemble_config = ert.ensembleConfig()

        assert "FOPT" in ensemble_config
        assert "WWCT" in ensemble_config
        assert "WOPR" in ensemble_config
        assert not "TCPU" in ensemble_config