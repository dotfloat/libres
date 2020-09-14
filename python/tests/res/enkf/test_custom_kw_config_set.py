import os
from tests import ResTest
from res.test.ert_test_context import ErtTestContext

from res.enkf import CustomKWConfigSet
from res.enkf.config import CustomKWConfig
from res.enkf.enkf_fs import EnkfFs
from res.enkf.enkf_main import EnKFMain
from ecl.util.util.stringlist import StringList

from tests.utils import tmpdir

class CustomKWConfigSetTest(ResTest):

    def createCustomKWConfig(self, name, data):
        self.createResultFile("result_file", data)

        config = CustomKWConfig(name, "")
        config.parseResultFile("result_file", StringList())

        return config

    def createResultFile(self, filename, data):
        with open(filename, "w") as output_file:
            for key in data:
                output_file.write("%s %s\n" % (key, data[key]))


    @tmpdir()
    def test_creation(self):
        config_set = CustomKWConfigSet()

        config = self.createCustomKWConfig("TEST", {"VALUE_1": 0.5, "VALUE_2": 5, "VALUE_3": "string", "VALUE_4": "true"})
        assert set(config.getKeys()) == set(["VALUE_1", "VALUE_2", "VALUE_3", "VALUE_4"])

        config_set.addConfig(config)
        keys = config_set.getStoredConfigKeys()
        assert set(keys) == set(["TEST"])

        config_set.reset()
        assert len(config_set.getStoredConfigKeys()) == 0


    @tmpdir()
    def test_fwrite_and_fread(self):
        trees_config = self.createCustomKWConfig("TREES", {"OAK": 0.1, "SPRUCE": 5, "FIR": "pines", "PALM": "coconut"})
        insects_config = self.createCustomKWConfig("INSECTS", {"MOSQUITO": "annoying", "FLY": 3.14, "BEETLE": 0.5})

        config_set = CustomKWConfigSet()
        config_set.addConfig(trees_config)
        config_set.addConfig(insects_config)

        assert set(config_set.getStoredConfigKeys()) == set(["TREES", "INSECTS"])

        config_set.fwrite("config_set")

        assert os.path.exists("config_set")

        config_set = CustomKWConfigSet("config_set")

        assert set(config_set.getStoredConfigKeys()) == set(["TREES", "INSECTS"])

        trees_config_from_file = CustomKWConfig("TREES", None)
        config_set.updateConfig(trees_config_from_file)

        for key in ["OAK", "SPRUCE", "FIR", "PALM"]:
            assert trees_config_from_file.indexOfKey(key) == trees_config.indexOfKey(key)
            assert trees_config_from_file.keyIsDouble(key) == trees_config.keyIsDouble(key)


        insects_config_from_file = CustomKWConfig("INSECTS", None)
        config_set.updateConfig(insects_config_from_file)

        for key in ["MOSQUITO", "FLY", "BEETLE"]:
            assert insects_config_from_file.indexOfKey(key) == insects_config.indexOfKey(key)
            assert insects_config_from_file.keyIsDouble(key) == insects_config.keyIsDouble(key)