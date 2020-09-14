import datetime

from ecl.util.util import BoolVector
from tests import ResTest
from res.enkf import ObsData, ObsBlock
from res.util import Matrix

class ObsDataTest(ResTest):


    def test_create(self):
        obs_data = ObsData()
        obs_size = 10
        block = obs_data.addBlock("OBS" , obs_size)
        assert  isinstance( block , ObsBlock )

        block[0] = (100,10)
        block[1] = (120,12)
        D = obs_data.createDObs()
        assert  isinstance(D , Matrix )
        assert D.dims() == (2,2)

        assert D[0,0] == 100
        assert D[1,0] == 120
        assert D[0,1] == 10
        assert D[1,1] == 12

        obs_data.scaleMatrix( D )
        assert D[0,0] == 10
        assert D[1,0] == 10
        assert D[0,1] == 1
        assert D[1,1] == 1

        R = obs_data.createR()
        assert (2,2) == R.dims()

        with pytest.raises(IndexError):
            obs_data[10]

        v,s = obs_data[0]
        assert v == 100
        assert s == 10


        v,s = obs_data[1]
        assert v == 120
        assert s == 12


