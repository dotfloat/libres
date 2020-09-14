#  Copyright (C) 2017  Equinor ASA, Norway.
#
#  The file 'test_model_config.py' is part of ERT - Ensemble based Reservoir Tool.
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
import os
from tests import ResTest, tmpdir
from res.enkf import ResConfig, ConfigKeys, ModelConfig
from res.sched import HistorySourceEnum
from res.test import ErtTestContext


class ModelConfigTest(ResTest):

    def setUp(self):
        self.config_both = {
                                "INTERNALS" :
                                {
                                  "CONFIG_DIRECTORY" : "simple_config",
                                },

                                "SIMULATION" :
                                {
                                  "QUEUE_SYSTEM" :
                                  {
                                    "JOBNAME" : "JOBNAME%d",
                                  },

                                  "RUNPATH"            : "/tmp/simulations/run%d",
                                  "NUM_REALIZATIONS"   : 1,
                                  "JOB_SCRIPT"         : "script.sh",
                                    "ENSPATH"          : "Ensemble",
                                  "ECLBASE"            : "ECLBASE%d"
                                }
                              }


        self.config_eclbase = {
                                "INTERNALS" :
                                {
                                  "CONFIG_DIRECTORY" : "simple_config",
                                },

                                "SIMULATION" :
                                {
                                  "RUNPATH"            : "/tmp/simulations/run%d",
                                  "NUM_REALIZATIONS"   : 1,
                                  "JOB_SCRIPT"         : "script.sh",
                                  "ENSPATH"            : "Ensemble",
                                  "ECLBASE"            : "ECLBASE%d"
                                }
                              }


        self.config_jobname = {
                                "INTERNALS" :
                                {
                                  "CONFIG_DIRECTORY" : "simple_config",
                                },

                                "SIMULATION" :
                                {
                                  "QUEUE_SYSTEM" :
                                  {
                                    "JOBNAME" : "JOBNAME%d",
                                  },

                                  "RUNPATH"            : "/tmp/simulations/run%d",
                                  "NUM_REALIZATIONS"   : 1,
                                  "JOB_SCRIPT"         : "script.sh",
                                  "ENSPATH"            : "Ensemble"
                                }
                              }



    @tmpdir(local="simple_config")
    def test_eclbase_and_jobname(self):
        res_config = ResConfig(config=self.config_both)
        model_config = res_config.model_config
        ecl_config = res_config.ecl_config

        assert  ecl_config.active( ) 
        assert "JOBNAME%d" == model_config.getJobnameFormat()

    @tmpdir(local="simple_config")
    def test_eclbase(self):
        res_config = ResConfig(config=self.config_eclbase)
        model_config = res_config.model_config
        ecl_config = res_config.ecl_config

        assert  ecl_config.active( ) 
        assert "ECLBASE%d" == model_config.getJobnameFormat( )

    @tmpdir(local="simple_config")
    def test_jobname(self):
        res_config = ResConfig(config=self.config_jobname)
        model_config = res_config.model_config
        ecl_config = res_config.ecl_config

        assert not  ecl_config.active( ) 
        assert "JOBNAME%d" == model_config.getJobnameFormat( )

    @tmpdir(local="configuration_tests")
    def test_model_config_dict_constructor(self):
        res_config = ResConfig(user_config_file="configuration_tests/model_config.ert")
        config_dict = {
            ConfigKeys.MAX_RESAMPLE: 1,
            ConfigKeys.JOBNAME: "model_config_test",
            ConfigKeys.RUNPATH: "/tmp/simulations/run%d",
            ConfigKeys.NUM_REALIZATIONS: 10,
            ConfigKeys.ENSPATH: "configuration_tests/Ensemble",
            ConfigKeys.TIME_MAP:"configuration_tests/input/refcase/time_map.txt",
            ConfigKeys.OBS_CONFIG: "configuration_tests/input/observations/observations.txt",
            ConfigKeys.DATAROOT: "configuration_tests/",
            ConfigKeys.HISTORY_SOURCE: 1,
            ConfigKeys.GEN_KW_EXPORT_NAME: "parameter_test.json",
            ConfigKeys.FORWARD_MODEL: [
                {
                    ConfigKeys.NAME: "COPY_FILE",
                    ConfigKeys.ARGLIST: "<FROM>=input/schedule.sch, <TO>=output/schedule_copy.sch",
                },
                {
                    ConfigKeys.NAME: "SNAKE_OIL_SIMULATOR",
                    ConfigKeys.ARGLIST : "",
                },
                {
                    ConfigKeys.NAME: "SNAKE_OIL_NPV",
                    ConfigKeys.ARGLIST: "",
                },
                {
                    ConfigKeys.NAME: "SNAKE_OIL_DIFF",
                    ConfigKeys.ARGLIST : "",
                }
            ]
        }
        model_config = ModelConfig(data_root="",
                                   joblist=res_config.site_config.get_installed_jobs(),
                                   last_history_restart=res_config.ecl_config.getLastHistoryRestart(),
                                   refcase=res_config.ecl_config.getRefcase(),
                                   config_dict=config_dict)
        assert model_config == res_config.model_config

    @tmpdir(local="configuration_tests")
    def test_schedule_file_as_history_is_disallowed(self):
        with self.assertRaises(ValueError) as cm:
            ResConfig(
                user_config_file="configuration_tests/sched_file_as_history_source.ert"
            )

        # Any assert should per the unittest documentation be outside the
        # scope of the assertRaises with-block.
        expected = "{} as {} is not supported".format(
            str(HistorySourceEnum.SCHEDULE), ConfigKeys.HISTORY_SOURCE
        )
        assert expected in str(cm.exception)