import pytest

from tests import ResTest
from tests.utils import tmpdir
from res.test import ErtTestContext

from ecl.grid import EclGrid
from ecl.summary import EclSum
from res.sched import History

from ecl.util.util import BoolVector,IntVector
from res.enkf import ActiveMode, EnsembleConfig
from res.enkf import (ObsVector, LocalObsdata, EnkfObs, TimeMap,
                      LocalObsdataNode, ObsData, MeasData, ActiveList)

@pytest.mark.equinor_test
class EnKFObsTest(ResTest):
    def setUp(self):
        self.config_file = self.createTestPath("Equinor/config/obs_testing/config")
        self.obs_config = self.createTestPath("Equinor/config/obs_testing/observations")
        self.obs_config2 = self.createTestPath("Equinor/config/obs_testing/observations2")
        self.refcase = self.createTestPath("Equinor/config/obs_testing/EXAMPLE_01_BASE")
        self.grid = self.createTestPath("Equinor/config/obs_testing/EXAMPLE_01_BASE.EGRID")

    @tmpdir()
    def test_scale_obs(self):
        with ErtTestContext("obs_test", self.config_file) as test_context:
            ert = test_context.getErt()
            obs = ert.getObservations()

            obs1 = obs["WWCT:OP_1"].getNode(50)
            obs2 = obs["WWCT:OP_1_50"].getNode(50)

            assert obs1.getStandardDeviation() == obs2.getStandardDeviation()
            std0 = obs1.getStandardDeviation()

            local_obsdata = LocalObsdata("obs", obs)
            node1 = local_obsdata.addNode("WWCT:OP_1")
            node2 = local_obsdata.addNode("WWCT:OP_1_50")
            node1.addTimeStep(50)
            node2.addTimeStep(50)

            mask = BoolVector(default_value=True)
            mask[2] = True
            meas_data = MeasData(mask)
            obs_data = ObsData()
            fs = ert.getEnkfFsManager().getCurrentFileSystem()
            active_list = IntVector()
            active_list.initRange(0,2,1)
            obs.getObservationAndMeasureData(fs, local_obsdata, active_list, meas_data, obs_data)
            assert 2 == len(obs_data)

            v1 = obs_data[0]
            v2 = obs_data[1]

            assert v1[1] == std0
            assert v2[1] == std0

            meas_data = MeasData(mask)
            obs_data = ObsData(10)
            obs.getObservationAndMeasureData(fs, local_obsdata, active_list, meas_data, obs_data)
            assert 2 == len(obs_data)

            v1 = obs_data[0]
            v2 = obs_data[1]

            assert v1[1] == std0*10
            assert v2[1] == std0*10

            actl = ActiveList()
            obs1.updateStdScaling(10, actl)
            obs2.updateStdScaling(20, actl)
            meas_data = MeasData(mask)
            obs_data = ObsData()
            obs.getObservationAndMeasureData(fs, local_obsdata, active_list, meas_data, obs_data)
            assert 2 == len(obs_data)

            v1 = obs_data[0]
            v2 = obs_data[1]

            assert v1[1] == std0*10
            assert v2[1] == std0*20

    @tmpdir()
    def testObs(self):
        with ErtTestContext("obs_test", self.config_file) as test_context:
            ert = test_context.getErt()
            obs = ert.getObservations()

            assert 32 == len(obs)
            for v in obs:
                assert isinstance(v, ObsVector)

            assert obs[-1].getKey() == 'RFT_TEST'
            assert obs[-1].getDataKey() == '4289383'
            assert obs[-1].getObsKey() == 'RFT_TEST'

            with pytest.raises(IndexError):
                v = obs[-40]
            with pytest.raises(IndexError):
                v = obs[40]

            with pytest.raises(KeyError):
                v = obs["No-this-does-not-exist"]

            v1 = obs["WWCT:OP_3"]
            v2 = obs["GOPT:OP"]
            mask = BoolVector(True, ert.getEnsembleSize())
            current_fs = ert.getEnkfFsManager().getCurrentFileSystem()

            assert v1.hasData(mask, current_fs)
            assert not v2.hasData(mask, current_fs)

            local_node = v1.createLocalObs()
            for t in v1.getStepList():
                assert local_node.tstepActive(t)

    @tmpdir()
    def test_obs_block_scale_std(self):
        with ErtTestContext("obs_test_scale", self.config_file) as test_context:
            ert = test_context.getErt()
            fs = ert.getEnkfFsManager().getCurrentFileSystem()
            active_list = IntVector()
            active_list.initRange(0, ert.getEnsembleSize(), 1)

            obs = ert.getObservations()
            obs_data = LocalObsdata("OBSxx", obs)
            obs_vector = obs["WWCT:OP_1"]
            obs_data.addObsVector(obs_vector)
            scale_factor = obs.scaleCorrelatedStd(fs, obs_data, active_list)

            for obs_node in obs_vector:
                for index in range(len(obs_node)):
                    assert scale_factor == obs_node.getStdScaling(index)




    def test_obs_block_all_active_local(self):
        with ErtTestContext("obs_test_all_active", self.config_file) as test_context:
            ert = test_context.getErt()
            obs = ert.getObservations()
            obs_data = obs.getAllActiveLocalObsdata()

            assert len(obs_data) == len(obs)
            for obs_vector in obs:
                assert obs_vector.getObservationKey() in obs_data

                tstep_list1 = obs_vector.getStepList()
                local_node = obs_data[ obs_vector.getObservationKey() ]
                for t in tstep_list1:
                    assert local_node.tstepActive(t)

                active_list = local_node.getActiveList()
                assert active_list.getMode() == ActiveMode.ALL_ACTIVE



    def test_create(self):
        ensemble_config = EnsembleConfig()
        obs = EnkfObs(ensemble_config)
        assert len(obs) == 0

        assert not obs.valid
        with pytest.raises(ValueError):
            obs.load(self.obs_config)
        assert len(obs) == 0


        time_map = TimeMap()
        obs = EnkfObs(ensemble_config, external_time_map=time_map)
        assert len(obs) == 0

        grid = EclGrid(self.grid)
        refcase = EclSum(self.refcase)

        history = History(refcase, False)
        obs = EnkfObs(ensemble_config, grid=grid, history=history)
        assert obs.valid
        with pytest.raises(IOError):
            obs.load("/does/not/exist")

        obs.load(self.obs_config)
        assert obs.valid
        assert len(obs) == 33
        obs.clear()
        assert len(obs) == 0

        obs.load(self.obs_config)
        assert len(obs) == 33
        assert "RFT2" not in obs
        obs.load(self.obs_config2)
        assert len(obs) == 35
        assert "RFT2" in obs

    def test_hookmanager_runpathlist(self):
        with ErtTestContext("obs_test", self.config_file) as test_context:
            ert = test_context.getErt()
            hm = ert.getHookManager()
            assert len(repr(hm)) > 0

            rpl = hm.getRunpathList()
            assert len(repr(rpl)) > 0

            ef = rpl.getExportFile()
            assert '.ert_runpath_list' in ef
            nf = 'myExportCamel'
            rpl.setExportFile('myExportCamel')
            ef = rpl.getExportFile()
            assert nf in ef



    def test_ert_obs_reload(self):
        with ErtTestContext("obs_test_reload", self.config_file) as test_context:
            ert = test_context.getErt()
            local_config = ert.getLocalConfig()
            update_step = local_config.getUpdatestep()
            mini_step = update_step[0]
            local_obs = mini_step.getLocalObsData()
            assert "WGOR:OP_5" in local_obs
            assert "RPR2_1" in local_obs


            ens_config = ert.ensembleConfig()
            wwct_op1 = ens_config["WWCT:OP_1"]
            wopr_op5 = ens_config["WOPR:OP_5"]

            obs = ert.getObservations()
            assert len(obs) == 32

            keys = wwct_op1.getObservationKeys()
            assert len(keys) == 2
            assert "WWCT:OP_1" in keys
            assert "WWCT:OP_1_50" in keys

            assert wopr_op5.getObservationKeys() == []

            ert.loadObservations("observations2")
            assert len(obs) == 2
            assert wwct_op1.getObservationKeys() == []
            assert wopr_op5.getObservationKeys() == ["WOPR:OP_5"]

            local_config = ert.getLocalConfig()
            update_step = local_config.getUpdatestep()
            mini_step = update_step[0]
            local_obs = mini_step.getLocalObsData()
            assert "WOPR:OP_5" in local_obs
            assert "RFT2" in local_obs
            assert not "WGOR:OP_5" in local_obs
            assert not "RPR2_1" in local_obs


            ert.loadObservations("observations", clear=False)
            assert len(obs) == 34
            keys = wwct_op1.getObservationKeys()
            assert len(keys) == 2
            assert "WWCT:OP_1" in keys
            assert "WWCT:OP_1_50" in keys

            assert wopr_op5.getObservationKeys() == ["WOPR:OP_5"]