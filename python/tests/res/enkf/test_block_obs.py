#  Copyright (C) 2015  Equinor ASA, Norway.
#
#  The file 'test_block_obs.py' is part of ERT - Ensemble based Reservoir Tool.
#
#  ERT is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ERT is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.
#
#  See the GNU General Public License at <http://www.gnu.org/licenses/gpl.html>
#  for more details.

import os

from res.enkf import BlockObservation
from res.enkf import ActiveList, FieldConfig
from tests import ResTest
from ecl.grid import EclGridGenerator


class BlockObsTest(ResTest):

    def test_create(self):
        grid = EclGridGenerator.create_rectangular( (10,20,5) , (1,1,1) )
        field_config = FieldConfig("PRESSURE" , grid)    
        block_obs = BlockObservation("P-CONFIG" , field_config , grid)

        assert len(block_obs) == 0

        block_obs.addPoint(1,2,3,100,25)
        assert len(block_obs) == 1
        assert block_obs.getValue(0) == 100
        assert block_obs.getStd(0) == 25
        assert block_obs.getStdScaling(0) == 1

        block_obs.addPoint(1,2,4,200,50)
        assert len(block_obs) == 2
        assert block_obs.getValue(1) == 200
        assert block_obs.getStd(1) == 50
        assert block_obs.getStdScaling(1) == 1

        active_list = ActiveList( )
        block_obs.updateStdScaling( 0.50 , active_list )
        assert block_obs.getStdScaling(0) == 0.50
        assert block_obs.getStdScaling(1) == 0.50

        active_list.addActiveIndex( 1 )
        block_obs.updateStdScaling( 2.00 , active_list )
        assert block_obs.getStdScaling(0) == 0.50
        assert block_obs.getStdScaling(1) == 2.00
        