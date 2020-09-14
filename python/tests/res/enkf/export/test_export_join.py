import pandas
import numpy
import os

from tests import ResTest
from res.test import ErtTestContext
from _pytest.monkeypatch import MonkeyPatch

from res.enkf.export import (DesignMatrixReader, SummaryCollector,
                             GenKwCollector, MisfitCollector)


def dumpDesignMatrix(path):
    with open(path, "w") as dm:
        dm.write("REALIZATION	EXTRA_FLOAT_COLUMN EXTRA_INT_COLUMN EXTRA_STRING_COLUMN\n")
        dm.write("0	0.08	125	ON\n")
        dm.write("1	0.07	225	OFF\n")
        dm.write("2	0.08	325	ON\n")
        dm.write("3	0.06	425	ON\n")
        dm.write("4	0.08	525	OFF\n")
        dm.write("5	0.08	625	ON\n")
        dm.write("6	0.09	725	ON\n")
        dm.write("7	0.08	825	OFF\n")
        dm.write("8	0.02	925	ON\n")
        dm.write("9	0.08	125	ON\n")
        dm.write("10	0.08	225	ON\n")
        dm.write("11	0.05	325	OFF\n")
        dm.write("12	0.08	425	ON\n")
        dm.write("13	0.07	525	ON\n")
        dm.write("14	0.08	625	UNKNOWN\n")
        dm.write("15	0.08	725	ON\n")
        dm.write("16	0.08	825	ON\n")
        dm.write("17	0.08	925	OFF\n")
        dm.write("18	0.09	125	ON\n")
        dm.write("19	0.08	225	ON\n")
        dm.write("20	0.06	325	OFF\n")
        dm.write("21	0.08	425	ON\n")
        dm.write("22	0.07	525	ON\n")
        dm.write("23	0.08	625	OFF\n")
        dm.write("24	0.08	725	ON\n")

class ExportJoinTest(ResTest):

    def setUp(self):
        self.monkeypatch = MonkeyPatch()
        self.monkeypatch.setenv("TZ", "CET") # The ert_statoil case was generated in CET
        self.config = self.createTestPath("local/snake_oil/snake_oil.ert")

    def tearDown(self):
        self.monkeypatch.undo()

    def test_join(self):

        with ErtTestContext("python/enkf/export/export_join", self.config) as context:
            dumpDesignMatrix("DesignMatrix.txt")
            ert = context.getErt()

            summary_data = SummaryCollector.loadAllSummaryData(ert, "default_1")
            gen_kw_data = GenKwCollector.loadAllGenKwData(ert, "default_1")
            misfit = MisfitCollector.loadAllMisfitData(ert, "default_1")
            dm = DesignMatrixReader.loadDesignMatrix("DesignMatrix.txt")

            result = summary_data.join(gen_kw_data, how='inner')
            result = result.join(misfit, how='inner')
            result = result.join(dm, how='inner')

            first_date = "2010-01-10"
            last_date = "2015-06-23"

            self.assertFloatEqual(result["SNAKE_OIL_PARAM:OP1_OCTAVES"][0][first_date], 3.947766)
            self.assertFloatEqual(result["SNAKE_OIL_PARAM:OP1_OCTAVES"][24][first_date], 4.206698)
            self.assertFloatEqual(result["SNAKE_OIL_PARAM:OP1_OCTAVES"][24][last_date], 4.206698)

            self.assertFloatEqual(result["EXTRA_FLOAT_COLUMN"][0][first_date], 0.08)
            assert result["EXTRA_INT_COLUMN"][0][first_date] == 125
            assert result["EXTRA_STRING_COLUMN"][0][first_date] == "ON"

            self.assertFloatEqual(result["EXTRA_FLOAT_COLUMN"][0][last_date], 0.08)
            assert result["EXTRA_INT_COLUMN"][0][last_date] == 125
            assert result["EXTRA_STRING_COLUMN"][0][last_date] == "ON"

            self.assertFloatEqual(result["EXTRA_FLOAT_COLUMN"][1][last_date], 0.07)
            assert result["EXTRA_INT_COLUMN"][1][last_date] == 225
            assert result["EXTRA_STRING_COLUMN"][1][last_date] == "OFF"

            self.assertFloatEqual(result["MISFIT:FOPR"][0][last_date], 457.491003)
            self.assertFloatEqual(result["MISFIT:FOPR"][24][last_date], 1630.774198)

            self.assertFloatEqual(result["MISFIT:TOTAL"][0][first_date], 468.469969)
            self.assertFloatEqual(result["MISFIT:TOTAL"][0][last_date], 468.469969)
            self.assertFloatEqual(result["MISFIT:TOTAL"][24][last_date], 1714.662370)


            with pytest.raises(KeyError):
                realization_13 = result.loc[60]

            column_count = len(result.columns)
            assert result.dtypes[0] == numpy.float64
            assert result.dtypes[column_count - 1] == numpy.object
            assert result.dtypes[column_count - 2] == numpy.int64