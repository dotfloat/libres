import pytest
from res.util import ArgPack
from ecl.util.util import StringList


def test_create():
    arg = ArgPack()
    assert len(arg) == 0

    arg.append(StringList())
    assert len(arg) == 1

    arg.append(3.14)
    assert len(arg) == 2

    o = object()
    with pytest.raises(TypeError):
        arg.append(o)


def test_args():
    arg = ArgPack(1, 2, 3)
    assert len(arg) == 3


def test_append_ptr():
    arg = ArgPack(StringList())
    assert len(arg) == 1
