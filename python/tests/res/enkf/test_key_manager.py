from res.enkf.key_manager import KeyManager
from res.test import ErtTestContext

from tests import ResTest

class KeyManagerTest(ResTest):
    def setUp(self):
        self.config_file = self.createTestPath("local/snake_oil/snake_oil.ert")

    def test_summary_keys(self):
        with ErtTestContext("enkf_key_manager_test", self.config_file) as testContext:
            ert = testContext.getErt()
            key_man = KeyManager(ert)

            assert len(key_man.summaryKeys()) == 47
            assert "FOPT" in key_man.summaryKeys()

            assert len(key_man.summaryKeysWithObservations()) == 2
            assert "FOPR" in key_man.summaryKeysWithObservations()
            assert key_man.isKeyWithObservations("FOPR")


    def test_gen_data_keys(self):
        with ErtTestContext("enkf_key_manager_test", self.config_file) as testContext:
            ert = testContext.getErt()
            key_man = KeyManager(ert)

            assert len(key_man.genDataKeys()) == 3
            assert "SNAKE_OIL_WPR_DIFF@199" in key_man.genDataKeys()

            assert len(key_man.genDataKeysWithObservations()) == 1
            assert "SNAKE_OIL_WPR_DIFF@199" in key_man.genDataKeysWithObservations()
            assert key_man.isKeyWithObservations("SNAKE_OIL_WPR_DIFF@199")

    def test_custom_keys(self):
        with ErtTestContext("enkf_key_manager_test", self.config_file) as testContext:
            ert = testContext.getErt()
            key_man = KeyManager(ert)

            assert len(key_man.customKwKeys()) == 2
            assert "SNAKE_OIL_NPV:NPV" in key_man.customKwKeys()

    def test_gen_kw_keys(self):
        with ErtTestContext("enkf_key_manager_test", self.config_file) as testContext:
            ert = testContext.getErt()
            key_man = KeyManager(ert)

            assert len(key_man.genKwKeys()) == 10
            assert "SNAKE_OIL_PARAM:BPR_555_PERSISTENCE" in key_man.genKwKeys()