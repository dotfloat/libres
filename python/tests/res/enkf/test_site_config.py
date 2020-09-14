#  Copyright (C) 2017  Equinor ASA, Norway.
#
#  The file 'test_site_config.py' is part of ERT - Ensemble based Reservoir Tool.
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

from res.enkf import SiteConfig, ConfigKeys
import os

from tests import ResTest, tmpdir

class SiteConfigTest(ResTest):

    def setUp(self):
        self.case_directory = self.createTestPath("local/simple_config/")
        self.snake_case_directory = self.createTestPath("local/snake_oil/")

    @tmpdir()
    def test_invalid_user_config(self):
        with pytest.raises(IOError):
            SiteConfig("this/is/not/a/file")

    @tmpdir(local="simple_config")
    def test_init(self):
        config_file = "simple_config/minimum_config"
        site_config = SiteConfig(user_config_file=config_file)
        assert site_config is not None

    @tmpdir(local="snake_oil")
    def test_constructors(self):
        config_file = "snake_oil/snake_oil.ert"

        ERT_SITE_CONFIG = SiteConfig.getLocation()
        ERT_SHARE_PATH = os.path.dirname(ERT_SITE_CONFIG)
        snake_config_dict = {
            ConfigKeys.INSTALL_JOB:
                [
                    {
                        ConfigKeys.NAME: "SNAKE_OIL_SIMULATOR",
                        ConfigKeys.PATH: os.getcwd() + "/snake_oil/jobs/SNAKE_OIL_SIMULATOR"
                    },
                    {
                        ConfigKeys.NAME: "SNAKE_OIL_NPV",
                        ConfigKeys.PATH: os.getcwd() + "/snake_oil/jobs/SNAKE_OIL_NPV"
                    },
                    {
                        ConfigKeys.NAME: "SNAKE_OIL_DIFF",
                        ConfigKeys.PATH: os.getcwd() + "/snake_oil/jobs/SNAKE_OIL_DIFF"
                    }
                ],
            ConfigKeys.INSTALL_JOB_DIRECTORY:
                [
                    ERT_SHARE_PATH + '/forward-models/res',
                    ERT_SHARE_PATH + '/forward-models/shell',
                    ERT_SHARE_PATH + '/forward-models/templating',
                    ERT_SHARE_PATH + '/forward-models/old_style'
                ],

            ConfigKeys.SETENV:
                [
                    {
                        ConfigKeys.NAME: "SILLY_VAR",
                        ConfigKeys.VALUE: "silly-value"
                    },
                    {
                        ConfigKeys.NAME: "OPTIONAL_VAR",
                        ConfigKeys.VALUE: "optional-value"
                    }
                ],
            ConfigKeys.LICENSE_PATH: "some/random/path",

            ConfigKeys.UMASK: 18
        }

        site_config_user_file = SiteConfig(user_config_file=config_file)
        site_config_dict = SiteConfig(config_dict=snake_config_dict)
        assert site_config_dict == site_config_user_file

        with pytest.raises(ValueError):
            site_config = SiteConfig(user_config_file=config_file, config_dict=snake_config_dict)