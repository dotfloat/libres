import os.path

from tests import ResTest, tmpdir
from res.enkf import GenObservation, GenDataConfig, ActiveList


class GenObsTest(ResTest):
    def setUp(self):
        pass


    @tmpdir()
    def test_create(self):
        data_config = GenDataConfig("KEY")
        with pytest.raises(ValueError):
            gen_obs = GenObservation("KEY" , data_config )

        with open("obs1.txt","w") as f:
            f.write("10  5  12 6\n")

        with pytest.raises(ValueError):
            gen_obs = GenObservation("KEY" , data_config , scalar_value = (1,2) , obs_file = "obs1.txt")

        with pytest.raises(TypeError):
            gen_obs = GenObservation("KEY" , data_config , scalar_value = 1 )

        with pytest.raises(IOError):
            gen_obs = GenObservation("KEY" , data_config , obs_file = "does/not/exist" )

        gen_obs = GenObservation("KEY" , data_config , obs_file = "obs1.txt" , data_index = "10,20")
        assert len(gen_obs) == 2
        assert gen_obs[0] == (10,5)
        assert gen_obs[1] == (12,6)

        assert gen_obs.getValue(0) == 10
        assert gen_obs.getDataIndex(1) == 20
        assert gen_obs.getStdScaling(0) == 1
        assert gen_obs.getStdScaling(1) == 1

        active_list = ActiveList( )
        gen_obs.updateStdScaling( 0.25 , active_list )
        assert gen_obs.getStdScaling(0) == 0.25
        assert gen_obs.getStdScaling(1) == 0.25

        active_list.addActiveIndex( 1 )
        gen_obs.updateStdScaling( 2.00 , active_list )
        assert gen_obs.getStdScaling(0) == 0.25
        assert gen_obs.getStdScaling(1) == 2.00