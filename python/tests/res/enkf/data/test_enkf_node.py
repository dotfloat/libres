import json
import os.path

from res.enkf.data import ExtParam
from res.enkf.data import EnkfNode
from res.enkf.config import ExtParamConfig, EnkfConfigNode


def test_config(tmpdir):
    with tmpdir.as_cwd():
        keys = ["Key1" , "Key2" , "Key3"]
        config = EnkfConfigNode.create_ext_param("key", keys)
        node = EnkfNode(config)
        ext_node = node.as_ext_param()
        ext_config = config.getModelConfig()

        ext_node.set_vector([1,2,3])
        node.ecl_write("path")
        d = json.load(open("path/key.json"))
        assert d["Key1"] == 1
        assert d["Key3"] == 3
