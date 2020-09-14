#  Copyright (C) 2012  Equinor ASA, Norway.
#
#  The file 'test_enkf.py' is part of ERT - Ensemble based Reservoir Tool.
#
#  ERT is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ERT is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.
#
#  See the GNU General Public License at <http://www.gnu.org/licenses/gpl.html>
#  for more details.

import sys, os
import os.path
import pytest
from tests import ResTest

from ecl.util.util import BoolVector
from res.enkf import (EnsembleConfig, AnalysisConfig, ModelConfig, SiteConfig,
                      EclConfig, EnkfObs, ErtTemplates, EnkfFs,
                      EnKFState, EnkfVarType, ObsVector, RunArg, ResConfig)
from res.enkf.config import EnkfConfigNode
from res.enkf.enkf_main import EnKFMain
from res.enkf.enums import (EnkfObservationImplementationType, LoadFailTypeEnum,
                            EnkfInitModeEnum, ErtImplType, RealizationStateEnum,
                            EnkfRunType, EnkfFieldFileFormatEnum,
                            EnkfTruncationType, ActiveMode)

from res.enkf.observations.summary_observation import SummaryObservation

from tests.utils import tmpdir

class EnKFTest(ResTest):
    @tmpdir(local="simple_config")
    def test_repr( self ):
        res_config = ResConfig("simple_config/minimum_config")
        main = EnKFMain(res_config)
        pfx = 'EnKFMain(ensemble_size'
        assert pfx == repr(main)[:len(pfx)]

    @tmpdir(local="simple_config")
    def test_bootstrap( self ):
        res_config = ResConfig("simple_config/minimum_config")
        main = EnKFMain(res_config)
        assert main, "Load failed"

    @tmpdir(local="simple_config")
    def test_site_condif(self):
        res_config = ResConfig("simple_config/minimum_config")
        main = EnKFMain(res_config)

        assert main, "Load failed"

        self.assertEqual(
                res_config.site_config_file,
                main.resConfig().site_config_file
                )

        self.assertEqual(
                res_config.user_config_file,
                main.resConfig().user_config_file
                )

    @tmpdir()
    def test_site_bootstrap( self ):
        with  self.assertRaises(ValueError):
            EnKFMain(None)

    @tmpdir(local="simple_config")
    def test_default_res_config(self):
        res_config = ResConfig("simple_config/minimum_config")
        main = EnKFMain(res_config)

        assert main.resConfig is not None
        assert main.siteConfig is not None
        assert main.analysisConfig is not None

    @tmpdir(local="simple_config")
    def test_invalid_res_config(self):
        with pytest.raises(TypeError):
            main = EnKFMain(res_config="This is not a ResConfig instance")

    @tmpdir()
    def test_enum(self):
        res_helper.assert_enum_fully_defined(EnkfVarType, "enkf_var_type", "lib/include/ert/enkf/enkf_types.hpp")
        res_helper.assert_enum_fully_defined(ErtImplType, "ert_impl_type", "lib/include/ert/enkf/enkf_types.hpp")
        res_helper.assert_enum_fully_defined(EnkfInitModeEnum, "init_mode_type", "lib/include/ert/enkf/enkf_types.hpp")
        res_helper.assert_enum_fully_defined(RealizationStateEnum, "realisation_state_enum", "lib/include/ert/enkf/enkf_types.hpp")
        res_helper.assert_enum_fully_defined(EnkfTruncationType, "truncation_type", "lib/include/ert/enkf/enkf_types.hpp")
        res_helper.assert_enum_fully_defined(EnkfRunType, "run_mode_type" , "lib/include/ert/enkf/enkf_types.hpp")

        res_helper.assert_enum_fully_defined(EnkfObservationImplementationType, "obs_impl_type", "lib/include/ert/enkf/obs_vector.hpp")
        res_helper.assert_enum_fully_defined(LoadFailTypeEnum, "load_fail_type", "lib/include/ert/enkf/summary_config.hpp")
        res_helper.assert_enum_fully_defined(EnkfFieldFileFormatEnum, "field_file_format_type", "lib/include/ert/enkf/field_config.hpp")
        res_helper.assert_enum_fully_defined(ActiveMode , "active_mode_type" , "lib/include/ert/enkf/enkf_types.hpp")

    @tmpdir(local="simple_config")
    def test_observations(self):
        res_config = ResConfig("simple_config/minimum_config")
        main = EnKFMain(res_config)

        count = 10
        summary_key = "test_key"
        observation_key = "test_obs_key"
        summary_observation_node = EnkfConfigNode.createSummaryConfigNode(summary_key, LoadFailTypeEnum.LOAD_FAIL_EXIT)
        observation_vector = ObsVector(EnkfObservationImplementationType.SUMMARY_OBS, observation_key, summary_observation_node, count)

        main.getObservations().addObservationVector(observation_vector)

        values = []
        for index in range(0, count):
            value = index * 10.5
            std = index / 10.0
            summary_observation_node = SummaryObservation(summary_key, observation_key, value, std)
            observation_vector.installNode(index, summary_observation_node)
            assert observation_vector.getNode(index) == summary_observation_node
            assert value == summary_observation_node.getValue()
            values.append((index, value, std))



        observations = main.getObservations()
        test_vector = observations[observation_key]
        index = 0
        for node in test_vector:
            assert  isinstance( node , SummaryObservation )
            assert node.getValue( ) == index * 10.5
            index += 1


        assert observation_vector == test_vector
        for index, value, std in values:
            assert test_vector.isActive(index)

            summary_observation_node = test_vector.getNode(index)
            """@type: SummaryObservation"""

            assert value == summary_observation_node.getValue()
            assert std == summary_observation_node.getStandardDeviation()
            assert summary_key == summary_observation_node.getSummaryKey()

    @tmpdir(local="simple_config")
    def test_config( self ):
        res_config = ResConfig("simple_config/minimum_config")
        main = EnKFMain(res_config)

        assert isinstance(main.ensembleConfig(), EnsembleConfig)
        assert isinstance(main.analysisConfig(), AnalysisConfig)
        assert isinstance(main.getModelConfig(), ModelConfig)
        assert isinstance(main.siteConfig(), SiteConfig)
        assert isinstance(main.eclConfig(), EclConfig)

        assert isinstance(main.getObservations(), EnkfObs)
        assert isinstance(main.get_templates(), ErtTemplates)
        assert isinstance(main.getEnkfFsManager().getCurrentFileSystem(), EnkfFs)
        assert isinstance(main.getMemberRunningState(0), EnKFState)

        assert "simple_config/Ensemble" == main.getMountPoint()


    @tmpdir()
    def test_enkf_create_config_file(self):
        config_file      = "test_new_config"
        dbase_type       = "BLOCK_FS"
        num_realizations = 42

        EnKFMain.createNewConfig(config_file, "storage" , dbase_type, num_realizations)
        res_config = ResConfig(config_file)
        main = EnKFMain(res_config)
        assert main.getEnsembleSize() == num_realizations


    @tmpdir(local="simple_config")
    def test_run_context(self):
        res_config = ResConfig("simple_config/minimum_config")
        main = EnKFMain(res_config)
        fs_manager = main.getEnkfFsManager()
        fs = fs_manager.getCurrentFileSystem( )
        iactive = BoolVector(initial_size = 10 , default_value = True)
        iactive[0] = False
        iactive[1] = False
        run_context = main.getRunContextENSEMPLE_EXPERIMENT( fs , iactive )

        assert len(run_context) == 10

        with pytest.raises(IndexError):
            run_context[10]

        with pytest.raises(TypeError):
            run_context["String"]

        assert  run_context[0]  is None
        run_arg = run_context[2]
        assert  isinstance( run_arg , RunArg )


    @tmpdir(local="snake_oil")
    def test_run_context_from_external_folder(self):
        res_config = ResConfig('snake_oil/snake_oil.ert')
        main = EnKFMain(res_config)
        fs_manager = main.getEnkfFsManager()
        fs = fs_manager.getCurrentFileSystem( )

        mask = BoolVector(default_value = False , initial_size = 10)
        mask[0] = True
        run_context = main.getRunContextENSEMPLE_EXPERIMENT( fs , mask )

        assert len(run_context) == 10

        job_queue = main.get_queue_config().create_job_queue()
        main.getEnkfSimulationRunner().createRunPath( run_context )
        num = main.getEnkfSimulationRunner().runEnsembleExperiment(job_queue, run_context)
        assert  os.path.isdir( "snake_oil/storage/snake_oil/runpath/realisation-0/iter-0")
        assert num == 1