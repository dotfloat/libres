import datetime

from ecl.util.util import BoolVector
from tests import ResTest
from res.enkf import ObsBlock



class ObsBlockTest(ResTest):


    def test_create(self):
        block = ObsBlock("OBS" , 1000)
        assert  isinstance( block , ObsBlock )
        assert 1000 == block.totalSize()
        assert 0 == block.activeSize()



    def test_access(self):
        obs_size = 10
        block = ObsBlock("OBS" , obs_size)

        with pytest.raises(IndexError):
            block[100] = (1,1)

        with pytest.raises(IndexError):
            block[-100] = (1,1)

        with pytest.raises(TypeError):
            block[4] = 10

        with pytest.raises(TypeError):
            block[4] = (1,1,9)

        #------

        with pytest.raises(IndexError):
            v = block[100]

        with pytest.raises(IndexError):
            v = block[-100]

        block[0] = (10,1)
        v = block[0]
        assert v == (10,1)
        assert 1 == block.activeSize()

        block[-1] = (17,19)
        assert block[-1] == (17,19)