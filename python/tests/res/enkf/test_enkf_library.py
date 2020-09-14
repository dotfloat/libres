import os
import pytest


from tests import ResTest
from tests.utils import tmpdir

from ecl.summary import EclSum
from res.enkf import AnalysisConfig, EclConfig, GenKwConfig, EnkfConfigNode, SiteConfig, ObsVector
from res.enkf import EnKFMain, ResConfig
from res.enkf import ErtTemplate, ErtTemplates, LocalConfig, ModelConfig
from res.enkf import GenDataConfig, FieldConfig, EnkfFs, EnkfObs, EnKFState, EnsembleConfig
from res.enkf.util import TimeMap


@pytest.mark.unstable
@pytest.mark.equinor_test
class EnKFLibraryTest(ResTest):
    def test_failed_class_creation(self):
        classes = [EnkfConfigNode, EnKFState,
                   ErtTemplate, LocalConfig]

        for cls in classes:
            with pytest.raises(NotImplementedError):
                temp = cls()

    @tmpdir(local="simple_config")
    def test_ecl_config_creation(self):
        res_config = ResConfig("simple_config/minimum_config")
        main = EnKFMain(res_config)

        assert isinstance(main.analysisConfig(), AnalysisConfig)
        assert isinstance(main.eclConfig(), EclConfig)

        with self.assertRaises(AssertionError): # Null pointer!
            assert isinstance(main.eclConfig().getRefcase(), EclSum)

        file_system = main.getEnkfFsManager().getCurrentFileSystem()
        assert file_system.getCaseName() == "default"
        time_map = file_system.getTimeMap()
        assert isinstance(time_map, TimeMap)