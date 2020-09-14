import datetime

from tests import ResTest
from ecl.util.util import BoolVector
from res.enkf import MeasBlock


class MeasBlockTest(ResTest):


    def test_create(self):
        key = "OBS"
        ens_size = 100
        obs_size = 77
        ens_mask = BoolVector( default_value = True , initial_size = ens_size )

        ens_mask[67] = False
        block = MeasBlock( key , obs_size , ens_mask)
        assert block.getObsSize() == obs_size
        assert block.getActiveEnsSize() == ens_size - 1
        assert block.getTotalEnsSize() == ens_size

        assert  block.iensActive( 66 ) 
        assert not  block.iensActive( 67 ) 




    def test_update(self):
        key = "OBS"
        obs_size = 4
        ens_size = 10
        ens_mask = BoolVector( default_value = True , initial_size = ens_size )
        block = MeasBlock( key , obs_size , ens_mask)

        with pytest.raises(TypeError):
            block["String"] = 10

        with pytest.raises(TypeError):
            block[10] = 10

        with pytest.raises(IndexError):
            block[obs_size,0] = 10

        with pytest.raises(IndexError):
            block[0,ens_size] = 10

        #-----------------------------------------------------------------

        with pytest.raises(TypeError):
            a = block["String"]

        with pytest.raises(TypeError):
            a = block[10]

        with pytest.raises(IndexError):
            val = block[obs_size,0]

        with pytest.raises(IndexError):
            val = block[0,ens_size]

        block[1,2] = 3
        assert 3 == block[1,2]



    def test_inactive(self):
        key = "OBS"
        obs_size = 2
        ens_size = 10
        ens_mask = BoolVector( default_value = True , initial_size = ens_size )
        ens_mask[5] = False
        block = MeasBlock( key , obs_size , ens_mask)

        assert not  block.iensActive( 5 )

        with pytest.raises(ValueError):
            block[0,5] = 10




    def test_stat(self):
        key = "OBS"
        obs_size = 2
        ens_size = 10
        ens_mask = BoolVector( default_value = True , initial_size = ens_size )
        block = MeasBlock( key , obs_size , ens_mask)

        for iens in range(ens_size):
            block[0,iens] = iens
            block[1,iens] = iens + 1

        assert 4.5 == block.igetMean( 0 )
        assert 5.5 == block.igetMean( 1 )

        self.assertFloatEqual( 2.872281 , block.igetStd( 0 ))
        self.assertFloatEqual( 2.872281 , block.igetStd( 1 ))


