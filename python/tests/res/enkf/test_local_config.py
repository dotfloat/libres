#  Copyright (C) 2017  Equinor ASA, Norway.
#
#  This file is part of ERT - Ensemble based Reservoir Tool.
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

import os.path

from tests import ResTest
from res.test import ErtTestContext

from res.enkf.local_ministep import LocalMinistep
from res.enkf.local_obsdata import LocalObsdata
from res.enkf.local_updatestep import LocalUpdateStep
from res.enkf.local_obsdata_node import LocalObsdataNode


class LocalConfigTest(ResTest):

    def setUp(self):
        self.config = self.createTestPath("local/custom_kw/mini_config")
        self.local_conf_path = 'python/enkf/data/local_config'


    def test_write_summary(self):
        with ErtTestContext(self.local_conf_path, self.config) as test_context:
            main = test_context.getErt()

            local_config = main.getLocalConfig()

            fname = "local_config_summary.txt"
            local_config.writeSummaryFile(fname)
            assert os.path.isfile(fname)


    def test_get_grid(self):
        with ErtTestContext(self.local_conf_path, self.config) as test_context:
            main = test_context.getErt()
            local_config = main.getLocalConfig()
            grid = local_config.getGrid()
            dimens = grid.getNX(), grid.getNY(), grid.getNZ()
            assert (10, 10, 5) == dimens


    def test_local_obs_data(self):
        with ErtTestContext(self.local_conf_path, self.config) as test_context:
            main = test_context.getErt()
            assert main, msg="Load failed"

            local_config = main.getLocalConfig()

            local_config.clear()
            updatestep = local_config.getUpdatestep()
            assert 0 == len(updatestep)

            # Creating obsdata
            local_obs_data_1 = local_config.createObsdata("OBSSET_1")
            assert isinstance(local_obs_data_1, LocalObsdata)

            # Try to add existing obsdata
            with pytest.raises(ValueError):
                local_config.createObsdata("OBSSET_1")

            # Add node with range
            with pytest.raises(KeyError):
                local_obs_data_1.addNodeAndRange("MISSING_KEY", 0, 1)

            local_obs_data_1.addNodeAndRange("GEN_PERLIN_1", 0, 1)
            local_obs_data_1.addNodeAndRange("GEN_PERLIN_2", 0, 1)
            assert len(local_obs_data_1) == 2

            # Delete node
            del local_obs_data_1["GEN_PERLIN_1"]
            assert len(local_obs_data_1) == 1

            # Get node
            node = local_obs_data_1["GEN_PERLIN_2"]
            assert isinstance(node, LocalObsdataNode)

            # Add node again with no range and check return type
            node_again = local_obs_data_1.addNode("GEN_PERLIN_1")
            assert isinstance(node_again, LocalObsdataNode)

            # Error when adding existing obs node
            with pytest.raises(KeyError):
                local_obs_data_1.addNode("GEN_PERLIN_1")


    def test_attach_obs_data(self):
        with ErtTestContext(self.local_conf_path, self.config) as test_context:
            main = test_context.getErt()

            local_config = main.getLocalConfig()
            local_obs_data_2 = local_config.createObsdata("OBSSET_2")
            assert isinstance(local_obs_data_2, LocalObsdata)

            # Obsdata
            local_obs_data_2.addNodeAndRange("GEN_PERLIN_1", 0, 1)
            local_obs_data_2.addNodeAndRange("GEN_PERLIN_2", 0, 1)

            # Ministep
            ministep = local_config.createMinistep("MINISTEP")
            assert isinstance(ministep, LocalMinistep)

            # Attach obsset
            ministep.attachObsset(local_obs_data_2)

            # Retrieve attached obsset
            local_obs_data_new = ministep.getLocalObsData()
            assert len(local_obs_data_new) == 2


    def test_all_active(self):
        with ErtTestContext(self.local_conf_path, self.config) as test_context:
            main = test_context.getErt()

            local_config = main.getLocalConfig()

            updatestep = local_config.getUpdatestep()
            ministep = updatestep[0]
            assert 1 == len(ministep)
            dataset = ministep["ALL_DATA"]
            assert "PERLIN_PARAM" in dataset

            obsdata = ministep.getLocalObsData()
            assert len(obsdata) == 3


    def test_ministep(self):
        with ErtTestContext("python/enkf/data/local_config", self.config) as test_context:
            main = test_context.getErt()

            local_config = main.getLocalConfig()
            analysis_module = main.analysisConfig().getModule("STD_ENKF")

            # Ministep
            ministep = local_config.createMinistep("MINISTEP", analysis_module)
            assert isinstance(ministep, LocalMinistep)

            assert not "DATA" in ministep
            with pytest.raises(KeyError):
                _ = ministep["DATA"]


    def test_attach_ministep(self):
        with ErtTestContext(self.local_conf_path, self.config) as test_context:
            main = test_context.getErt()

            local_config = main.getLocalConfig()

            # Update step
            updatestep = local_config.getUpdatestep()
            assert isinstance(updatestep, LocalUpdateStep)
            upd_size = len(updatestep)

            # Ministep
            ministep = local_config.createMinistep("MINISTEP")
            assert isinstance(ministep, LocalMinistep)

            # Attach
            updatestep.attachMinistep(ministep)
            assert isinstance(updatestep[0], LocalMinistep)
            assert len(updatestep) == upd_size + 1