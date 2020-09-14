#!/usr/bin/env python
#  Copyright (C) 2015  Equinor ASA, Norway.
#
#  The file 'test_linalg.py' is part of ERT - Ensemble based Reservoir Tool.
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


from res.enkf import ObsVector
from res.util import Matrix
from res.analysis import Linalg
from tests import ResTest

class LinalgTest(ResTest):

    def test_num_PC(self):
        S = Matrix(3,3)
        S[0,0] = 1
        S[1,1] = 1
        S[2,2] = 1

        with pytest.raises(ValueError):
            num_pc = Linalg.numPC( S , 0 )

        with pytest.raises(ValueError):
            num_pc = Linalg.numPC( S , 1.5 )

        num_pc = Linalg.numPC( S , 0.20 )
        assert num_pc == 1

        num_pc = Linalg.numPC( S , 0.50 )
        assert num_pc == 2

        num_pc = Linalg.numPC( S , 0.80 )
        assert num_pc == 3

