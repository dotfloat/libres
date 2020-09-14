from tests import ResTest
from res.test import ErtTestContext

from res.enkf.export import GenDataCollector


class GenDataCollectorTest(ResTest):
    def test_gen_data_collector(self):
        config = self.createTestPath("local/snake_oil/snake_oil.ert")
        with ErtTestContext("python/enkf/export/gen_data_collector", config) as context:
            ert = context.getErt()

            with pytest.raises(KeyError):
                data = GenDataCollector.loadGenData(ert, "default_0", "RFT_XX", 199)

            with pytest.raises(ValueError):
                data = GenDataCollector.loadGenData(ert, "default_0", "SNAKE_OIL_OPR_DIFF", 198)

            data1 = GenDataCollector.loadGenData(ert, "default_0", "SNAKE_OIL_OPR_DIFF", 199)

            self.assertFloatEqual(data1[0][0], -0.008206)
            self.assertFloatEqual(data1[24][1], -0.119255)
            self.assertFloatEqual(data1[24][1000], -0.258516)