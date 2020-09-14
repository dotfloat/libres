from tests import ResTest
from res.test import ErtTestContext

from res.enkf.export import GenDataObservationCollector


class GenDataObservationCollectorTest(ResTest):

    def test_gen_data_collector(self):
        config = self.createTestPath("local/custom_kw/mini_config")
        with ErtTestContext("python/enkf/export/gen_data_observation_collector", config) as context:
            ert = context.getErt()

            obs_key = GenDataObservationCollector.getObservationKeyForDataKey(ert, "PERLIN", 1)
            assert obs_key == "GEN_PERLIN_1"

            obs_key = GenDataObservationCollector.getObservationKeyForDataKey(ert, "PERLIN", 2)
            assert obs_key == "GEN_PERLIN_2"

            obs_key = GenDataObservationCollector.getObservationKeyForDataKey(ert, "PERLIN", 3)
            assert obs_key == "GEN_PERLIN_3"

            obs_key = GenDataObservationCollector.getObservationKeyForDataKey(ert, "PERLIN", 4)
            assert obs_key is None

            obs_key = GenDataObservationCollector.getObservationKeyForDataKey(ert, "PERLINk", 1)
            assert obs_key is None

            data = GenDataObservationCollector.loadGenDataObservations(ert, "default", "GEN_PERLIN_1")

            self.assertFloatEqual(data["GEN_PERLIN_1"][0], -0.616789)
            self.assertFloatEqual(data["STD_GEN_PERLIN_1"][0], 0.2)

            with pytest.raises(KeyError):
                GenDataObservationCollector.loadGenDataObservations(ert, "default", "GEN_PERLIN_4")