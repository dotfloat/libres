import os
from tests import ResTest
from res.test import ErtTestContext
from _pytest.monkeypatch import MonkeyPatch

from res.enkf.export import SummaryObservationCollector


class SummaryObservationCollectorTest(ResTest):

    def setUp(self):
        self.monkeypatch = MonkeyPatch()
        self.monkeypatch.setenv("TZ", "CET") # The ert_statoil case was generated in CET
        self.config = self.createTestPath("local/snake_oil/snake_oil.ert")


    def tearDown(self):
        self.monkeypatch.undo()


    def test_summary_observation_collector(self):

        with ErtTestContext("python/enkf/export/summary_observation_collector", self.config) as context:

            ert = context.getErt()

            assert SummaryObservationCollector.summaryKeyHasObservations(ert, "FOPR")
            assert not SummaryObservationCollector.summaryKeyHasObservations(ert, "FOPT")

            keys = SummaryObservationCollector.getAllObservationKeys(ert)
            assert "FOPR" in keys
            assert "WOPR:OP1" in keys
            assert not "WOPR:OP2" in keys

            data = SummaryObservationCollector.loadObservationData(ert, "default_0")

            self.assertFloatEqual(data["FOPR"]["2010-01-10"],  0.001696887)
            self.assertFloatEqual(data["STD_FOPR"]["2010-01-10"], 0.1)

            self.assertFloatEqual(data["WOPR:OP1"]["2010-03-31"], 0.1)
            self.assertFloatEqual(data["STD_WOPR:OP1"]["2010-03-31"], 0.05)


            with pytest.raises(KeyError):
                fgir = data["FGIR"]


            data = SummaryObservationCollector.loadObservationData(ert, "default_0", ["WOPR:OP1"])

            self.assertFloatEqual(data["WOPR:OP1"]["2010-03-31"], 0.1)
            self.assertFloatEqual(data["STD_WOPR:OP1"]["2010-03-31"], 0.05)

            with pytest.raises(KeyError):
                data["FOPR"]