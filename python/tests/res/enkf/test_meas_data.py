import datetime

from ecl.util.util import BoolVector
from tests import ResTest
from res.enkf import MeasBlock, MeasData


class MeasDataTest(ResTest):


    def test_create(self):
        ens_size = 10
        ens_mask = BoolVector( default_value = True , initial_size = ens_size )
        data = MeasData( ens_mask )
        assert len(data) == 0
        assert  isinstance( data , MeasData )

        block1 = data.addBlock( "OBS1" , 10 , 5 )
        block2 = data.addBlock( "OBS2" , 27 , 10 )

        with pytest.raises(TypeError):
            data[1.782]

        with pytest.raises(KeyError):
            data["NO-this-does-not-exist"]

        with pytest.raises(IndexError):
            data[2]

        last0 = data[-1]
        last1 = data[1]
        assert last0 == last1

        assert  "OBS1-10" in data 
        assert  "OBS2-27" in data 
        assert len(data) == 2

        assert  isinstance( block1 , MeasBlock )
        assert  isinstance( block2 , MeasBlock )

        assert block1.getObsSize() == 5
        assert block2.getObsSize() == 10

        l = []
        for b in data:
            l.append(b)

        assert len(l) == 2
        assert l[0] == block1
        assert l[1] == block2


        with pytest.raises(ValueError):
            S = data.createS()

        for iens in range(ens_size):
            block1[0,iens] = 5
            block2[0,iens] = 10
            block2[1,iens] = 15

        assert 3 == data.activeObsSize()
        S = data.createS()

        assert S.dims() == (3 , ens_size)

        for iens in range(ens_size):
            assert S[0,iens] == 5
            assert S[1,iens] == 10
            assert S[2,iens] == 15

        pfx = 'MeasData(len = '
        assert pfx == repr(data)[:len(pfx)]