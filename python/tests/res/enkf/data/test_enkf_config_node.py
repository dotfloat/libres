import os.path
import json

from res.enkf.config import EnkfConfigNode
from tests import ResTest


class EnkfConfigNodeTest(ResTest):
    def test_gen_data(self):

        # Must have %d in filename argument
        with pytest.raises(ValueError):
            config_node = EnkfConfigNode.create_gen_data( "KEY", "FILE" )

        config_node = EnkfConfigNode.create_gen_data( "KEY", "FILE%d" )
        assert isinstance( config_node, EnkfConfigNode )
        gen_data = config_node.getModelConfig( )
        assert 1 == gen_data.getNumReportStep( )
        assert 0 == gen_data.getReportStep(0)

        config_node = EnkfConfigNode.create_gen_data( "KEY", "FILE%d" , report_steps = [10,20,30])
        assert isinstance( config_node, EnkfConfigNode )
        gen_data = config_node.getModelConfig( )
        assert 3 == gen_data.getNumReportStep( )
        for r1,r2 in zip([10,20,30] , gen_data.getReportSteps()):
            assert r1 == r2
