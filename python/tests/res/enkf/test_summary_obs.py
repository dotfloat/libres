#  Copyright (C) 2015  Equinor ASA, Norway.
#
#  The file 'test_summary_obs.py' is part of ERT - Ensemble based Reservoir Tool.
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

from res.enkf import SummaryObservation
from res.enkf import ActiveList
from tests import ResTest



class SummaryObsTest(ResTest):

    def test_create(self):
        sum_obs = SummaryObservation("WWCT:OP_X" , "WWCT:OP_X" , 0.25 , 0.12)

        assert sum_obs.getValue() == 0.25
        assert sum_obs.getStandardDeviation() == 0.12
        assert sum_obs.getStdScaling() == 1.0


    def test_std_scaling(self):
        sum_obs = SummaryObservation("WWCT:OP_X" , "WWCT:OP_X" , 0.25 , 0.12)

        active_list = ActiveList()
        sum_obs.updateStdScaling(0.50 , active_list)
        sum_obs.updateStdScaling(0.125 , active_list)
        assert sum_obs.getStdScaling() == 0.125