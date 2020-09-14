#  Copyright (C) 2015  Equinor ASA, Norway.
#
#  The file 'test_active_list.py' is part of ERT - Ensemble based Reservoir Tool.
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

from res.enkf import ActiveList
from res.enkf import ActiveMode


def test_active_mode_enum():
    assert ActiveMode.ALL_ACTIVE == 1
    assert ActiveMode.INACTIVE == 2
    assert ActiveMode.PARTLY_ACTIVE == 3
    assert ActiveMode(1).name == 'ALL_ACTIVE'
    assert ActiveMode(2).name == 'INACTIVE'
    assert ActiveMode(3).name == 'PARTLY_ACTIVE'


def test_active_size():
    al = ActiveList()
    assert al.getActiveSize() is None
    assert 7 == al.getActiveSize(7)
    assert -1 == al.getActiveSize(-1)

    al.addActiveIndex(10)
    assert 1 == al.getActiveSize(7)
    al.addActiveIndex(10)
    assert 1 == al.getActiveSize(7)
    al.addActiveIndex(100)
    assert 2 == al.getActiveSize(7)


def test_create():
    active_list = ActiveList()
    assert active_list.getMode() == ActiveMode.ALL_ACTIVE
    active_list.addActiveIndex(10)
    assert active_list.getMode() == ActiveMode.PARTLY_ACTIVE


def test_repr():
    al = ActiveList()
    rep = repr(al)
    assert 'PARTLY_ACTIVE' not in rep
    assert 'INACTIVE' not in rep
    assert 'ALL_ACTIVE' in rep
    pfx = 'ActiveList('
    assert pfx == rep[:len(pfx)]
    for i in range(150):
        al.addActiveIndex(3*i)
    rep = repr(al)
    assert '150' in rep
    assert 'PARTLY_ACTIVE' in rep
    assert 'INACTIVE' not in rep
    assert 'ALL_ACTIVE' not in rep
