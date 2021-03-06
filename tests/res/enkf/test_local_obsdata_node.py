from res.enkf import LocalObsdataNode
from tests import ResTest


class LocalObsdataNodeTest(ResTest):
    def setUp(self):
        pass

    def test_tstep(self):
        node = LocalObsdataNode("KEY")
        self.assertTrue(node.allTimeStepActive())
        self.assertTrue(node.tstepActive(10))
        self.assertTrue(node.tstepActive(0))

        node.addTimeStep(10)
        self.assertFalse(node.allTimeStepActive())

        self.assertTrue(node.tstepActive(10))
        self.assertFalse(node.tstepActive(0))
