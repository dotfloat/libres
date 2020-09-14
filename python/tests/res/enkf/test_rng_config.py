#  Copyright (C) 2017  Equinor ASA, Norway.
#
#  The file 'test_rng_config.py' is part of ERT - Ensemble based Reservoir Tool.
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

from res.enkf import ResConfig, EnKFMain, RNGConfig, ConfigKeys

class RNGConfigTest(ResTest):


    def create_base_config(self):
        return {
                 "INTERNALS" :
                 {
                   "CONFIG_DIRECTORY" : "simple_config",
                 },

                 "SIMULATION" :
                 {
                   "QUEUE_SYSTEM" :
                   {
                     "JOBNAME" : "Job%d",
                   },

                   "RUNPATH"            : "/tmp/simulations/run%d",
                   "NUM_REALIZATIONS"   : 1,
                   "JOB_SCRIPT"         : "script.sh",
                   "ENSPATH"            : "Ensemble",
                   "LOGGING" : { "LOG_LEVEL" : "DEBUG" }
                 }
               }


    @tmpdir(local="simple_config")
    def test_load_seed(self):
        config = self.create_base_config()

        seed_store = "../input/rng/SEED_STORE"
        seed_load = "../input/rng/SEED"
        config["SIMULATION"]["SEED"] = { "STORE_SEED" : seed_store,
                                         "LOAD_SEED"  : seed_load }

        res_config = ResConfig(config=config)

        self.assertEqual(seed_load,
                         res_config.rng_config.load_filename)

        self.assertEqual(seed_store,
                         res_config.rng_config.store_filename)

        assert res_config.rng_config.random_seed is None

    @tmpdir(local="simple_config")
    def test_dict_constructor(self):
        config = self.create_base_config()

        seed_store = "../input/rng/SEED_STORE"
        seed_load = "../input/rng/SEED"
        config["SIMULATION"]["SEED"] = {ConfigKeys.STORE_SEED: seed_store,
                                        ConfigKeys.LOAD_SEED: seed_load}
        rng_config = RNGConfig(config_dict=config["SIMULATION"]["SEED"])
        res_config = ResConfig(config=config)
        assert rng_config == res_config.rng_config

        random_seed = "abcdefghijklmnop"
        config["SIMULATION"]["SEED"] = {ConfigKeys.RANDOM_SEED: random_seed}

        rng_config = RNGConfig(config_dict=config["SIMULATION"]["SEED"])
        res_config = ResConfig(config=config)
        assert rng_config == res_config.rng_config

        #seed store and seed load should be ignored by both constructors
        config["SIMULATION"]["SEED"] = {ConfigKeys.RANDOM_SEED: random_seed,
                                    ConfigKeys.STORE_SEED: seed_store,
                                    ConfigKeys.LOAD_SEED: seed_load
                                    }

        rng_config = RNGConfig(config_dict=config["SIMULATION"]["SEED"])
        res_config = ResConfig(config=config)
        assert rng_config == res_config.rng_config

    @tmpdir(local="simple_config")
    def test_random_seed(self):
        config = self.create_base_config()

        random_seed = "abcdefghijklmnop"
        config["SIMULATION"]["SEED"] = { ConfigKeys.RANDOM_SEED : random_seed }

        res_config = ResConfig(config=config)

        assert res_config.rng_config.load_filename is None
        assert res_config.rng_config.store_filename is None

        assert random_seed == res_config.rng_config.random_seed


    @tmpdir(local="simple_config")
    def test_seed_conflict(self):
        config = self.create_base_config()

        seed_store = "../input/rng/SEED_STORE"
        seed_load = "../input/rng/SEED"
        random_seed = "abcdefghijklmnop"
        config["SIMULATION"]["SEED"] = { "STORE_SEED" : seed_store,
                                         "LOAD_SEED"  : seed_load,
                                         ConfigKeys.RANDOM_SEED : random_seed }

        res_config = ResConfig(config=config)

        assert res_config.rng_config.load_filename is None
        assert res_config.rng_config.store_filename is None

        assert random_seed == res_config.rng_config.random_seed