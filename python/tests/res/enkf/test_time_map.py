import datetime

from res.enkf.enums.realization_state_enum import RealizationStateEnum
from res.enkf import TimeMap
from tests import ResTest
from tests.utils import tmp


class TimeMapTest(ResTest):

    def test_time_map(self):
        with pytest.raises(IOError):
            TimeMap("Does/not/exist")


        tm = TimeMap()
        with pytest.raises(IndexError):
            t = tm[10]

        pfx = 'TimeMap('
        rep = repr(tm)
        print('repr(time_map) = "%s"' % repr(tm))
        assert pfx == rep[:len(pfx)]

        assert  tm.update(0 , datetime.date(2000 , 1, 1))
        assert tm[0] == datetime.date(2000 , 1, 1)

        assert  tm.isStrict() 
        with pytest.raises(Exception):
            tm.update(0 , datetime.date(2000 , 1, 2))

        tm.setStrict( False )
        assert not tm.update(0 , datetime.date(2000 , 1, 2))

        tm.setStrict( True )
        assert  tm.update( 1 , datetime.date(2000 , 1, 2))
        d = tm.dump()
        self.assertEqual( d , [(0 , datetime.date(2000,1,1) , 0),
                               (1 , datetime.date(2000,1,2) , 1)])


    def test_fscanf(self):
        tm = TimeMap()

        with pytest.raises(IOError):
            tm.fload( "Does/not/exist" )

        with tmp():
            with open("map.txt","w") as fileH:
                fileH.write("10/10/2000\n")
                fileH.write("12/10/2000\n")
                fileH.write("14/10/2000\n")
                fileH.write("16/10/2000\n")

            tm.fload("map.txt")
            assert 4 == len(tm)
            assert datetime.date(2000,10,10) == tm[0]
            assert datetime.date(2000,10,16) == tm[3]

        with tmp():
            with open("map.txt","w") as fileH:
                fileH.write("10/10/200X\n")

            with pytest.raises(Exception):
                tm.fload("map.txt")

            assert 4 == len(tm)
            assert datetime.date(2000,10,10) == tm[0]
            assert datetime.date(2000,10,16) == tm[3]


        with tmp():
            with open("map.txt","w") as fileH:
                fileH.write("12/10/2000\n")
                fileH.write("10/10/2000\n")

            with pytest.raises(Exception):
                tm.fload("map.txt")

            assert 4 == len(tm)
            assert datetime.date(2000,10,10) == tm[0]
            assert datetime.date(2000,10,16) == tm[3]


    def test_setitem(self):
        tm = TimeMap()
        tm[0] = datetime.date(2000,1,1)
        tm[1] = datetime.date(2000,1,2)
        assert 2 == len(tm)

        assert tm[0] == datetime.date(2000,1,1)
        assert tm[1] == datetime.date(2000,1,2)


    def test_in(self):
        tm = TimeMap()
        tm[0] = datetime.date(2000,1,1)
        tm[1] = datetime.date(2000,1,2)
        tm[2] = datetime.date(2000,1,3)

        assert  datetime.date(2000,1,1) in tm 
        assert  datetime.date(2000,1,2) in tm 
        assert  datetime.date(2000,1,3) in tm 

        assert not  datetime.date(2001,1,3) in tm 
        assert not  datetime.date(1999,1,3) in tm 


    def test_lookupDate(self):
        tm = TimeMap()
        tm[0] = datetime.date(2000,1,1)
        tm[1] = datetime.date(2000,1,2)
        tm[2] = datetime.date(2000,1,3)

        assert 0 == tm.lookupTime( datetime.date(2000,1,1))
        assert 0 == tm.lookupTime( datetime.datetime(2000,1,1,0,0,0))

        assert 2 == tm.lookupTime( datetime.date(2000,1,3))
        assert 2 == tm.lookupTime( datetime.datetime(2000,1,3,0,0,0))

        with pytest.raises(ValueError):
            tm.lookupTime( datetime.date(1999,10,10))



    def test_lookupDays(self):
        tm = TimeMap()

        with pytest.raises(ValueError):
            tm.lookupDays( 0  )

        tm[0] = datetime.date(2000,1,1)
        tm[1] = datetime.date(2000,1,2)
        tm[2] = datetime.date(2000,1,3)

        assert 0 == tm.lookupDays( 0 )
        assert 1 == tm.lookupDays( 1 )
        assert 2 == tm.lookupDays( 2 )

        with pytest.raises(ValueError):
            tm.lookupDays( -1  )

        with pytest.raises(ValueError):
            tm.lookupDays( 0.50  )

        with pytest.raises(ValueError):
            tm.lookupDays( 3  )



    def test_nearest_date_lookup(self):
        tm = TimeMap()
        with pytest.raises(ValueError):
            tm.lookupTime(datetime.date( 1999 , 1 , 1))

        with pytest.raises(ValueError):
            tm.lookupTime(datetime.date( 1999 , 1 , 1) , tolerance_seconds_before = 10 , tolerance_seconds_after = 10)

        tm[0] = datetime.date(2000,1,1)
        tm[1] = datetime.date(2000,2,1)
        tm[2] = datetime.date(2000,3,1)

        # Outside of total range will raise an exception, irrespective of
        # the tolerances used.
        with pytest.raises(ValueError):
            tm.lookupTime(datetime.date( 1999 , 1 , 1) , tolerance_seconds_before = -1 , tolerance_seconds_after = -1)

        with pytest.raises(ValueError):
            tm.lookupTime(datetime.date( 2001 , 1 , 1) , tolerance_seconds_before = -1 , tolerance_seconds_after = -1)

        assert 0 == tm.lookupTime( datetime.datetime(2000 , 1 , 1 , 0 , 0 , 10) , tolerance_seconds_after = 15)
        assert 1 == tm.lookupTime( datetime.datetime(2000 , 1 , 1 , 0 , 0 , 10) , tolerance_seconds_before = 3600*24*40)

        assert 0 == tm.lookupTime( datetime.date( 2000 , 1 , 10) , tolerance_seconds_before = -1 , tolerance_seconds_after = -1)
        assert 1 == tm.lookupTime( datetime.date( 2000 , 1 , 20) , tolerance_seconds_before = -1 , tolerance_seconds_after = -1)

        with pytest.raises(ValueError):
            tm.lookupTime(datetime.date( 2001 , 10 , 1) , tolerance_seconds_before = 10 , tolerance_seconds_after = 10)


    def test_empty(self):
        tm = TimeMap()
        last_step = tm.getLastStep( )
        assert last_step == -1