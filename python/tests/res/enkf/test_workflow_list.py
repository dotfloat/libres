#  Copyright (C) 2017  Equinor ASA, Norway.
#
#  The file 'test_summary_obs.py' is part of ERT - Ensemble based Reservoir Tool.
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
from res.enkf import ErtWorkflowList, ResConfig, SiteConfig, ConfigKeys


class ErtWorkflowListTest(ResTest):
    def setUp(self):
        self.case_directory = self.createTestPath("local/simple_config/")

    @tmpdir(local="simple_config")
    def test_workflow_list_constructor(self):
        ERT_SITE_CONFIG = SiteConfig.getLocation()
        ERT_SHARE_PATH = os.path.dirname(ERT_SITE_CONFIG)

        self.config_dict = {
            ConfigKeys.LOAD_WORKFLOW_JOB:
                [
                    {
                        ConfigKeys.NAME: "print_uber",
                        ConfigKeys.PATH: os.getcwd() + "/simple_config/workflows/UBER_PRINT"
                    }
                ],

            ConfigKeys.LOAD_WORKFLOW:
                [
                    {
                        ConfigKeys.NAME: "magic_print",
                        ConfigKeys.PATH: os.getcwd() + "/simple_config/workflows/MAGIC_PRINT"
                    }
                ],
            ConfigKeys.WORKFLOW_JOB_DIRECTORY: [
                    ERT_SHARE_PATH + '/workflows/jobs/internal/config',
                    ERT_SHARE_PATH + '/workflows/jobs/internal-gui/config'
                ],
        }

        config_file = "simple_config/minimum_config"
        with open(config_file,'a+') as ert_file:
            ert_file.write("LOAD_WORKFLOW_JOB workflows/UBER_PRINT print_uber\n")
            ert_file.write("LOAD_WORKFLOW workflows/MAGIC_PRINT magic_print\n")

        os.mkdir("simple_config/workflows")

        with open("simple_config/workflows/MAGIC_PRINT","w") as f:
            f.write("print_uber\n")
        with open("simple_config/workflows/UBER_PRINT", "w") as f:
            f.write("EXECUTABLE ls\n")

        res_config = ResConfig(config_file)
        list_from_content = res_config.ert_workflow_list
        list_from_dict = ErtWorkflowList(subst_list=res_config.subst_config.subst_list, config_dict=self.config_dict)
        assert list_from_content == list_from_dict

    def test_illegal_configs(self):
        with pytest.raises(ValueError):
            ErtWorkflowList(subst_list=[], config_dict=[], config_content=[])

        with pytest.raises(ValueError):
            ErtWorkflowList()