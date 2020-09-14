from res.enkf import LocalObsdataNode
from tests import ResTest


class LocalObsdataNodeTest(ResTest):
    def setUp(self):
        pass

    def test_tstep(self):
        node = LocalObsdataNode("KEY")
        assert  node.allTimeStepActive() 
        assert  node.tstepActive( 10 )
        assert  node.tstepActive( 0 )

        node.addTimeStep(10)
        assert not  node.allTimeStepActive() 

        assert  node.tstepActive( 10 )
        assert not  node.tstepActive( 0 )


