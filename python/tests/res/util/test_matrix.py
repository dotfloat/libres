import pytest
from ecl.util.util import RandomNumberGenerator
from ecl.util.enums import RngAlgTypeEnum, RngInitModeEnum
from res.util import Matrix
from cwrap import CFILE, BaseCClass, load, open as copen


def test_matrix():
    m = Matrix(2, 3)

    assert m.rows() == 2
    assert m.columns() == 3
    assert m[(0, 0)] == 0

    m[(1, 1)] = 1.5
    assert m[(1, 1)] == 1.5

    m[1,0] = 5
    assert m[(1, 0)] == 5

    with pytest.raises(TypeError):
        m[5] = 5

    with pytest.raises(IndexError):
        m[2, 0] = 0

    with pytest.raises(IndexError):
        m[0, 3] = 0


def test_matrix_set():
    m1 = Matrix(2,2)
    m1.setAll(99)
    assert m1[0, 0] == 99
    assert m1[1, 1] == 99

    m2 = Matrix(2,2 , value = 99)
    assert m1 == m2


def test_matrix_random_init():
    m = Matrix(10,10)
    rng = RandomNumberGenerator(RngAlgTypeEnum.MZRAN, RngInitModeEnum.INIT_DEFAULT)
    m.randomInit( rng )


def test_matrix_copy_column():
    m = Matrix(10,2)
    rng = RandomNumberGenerator(RngAlgTypeEnum.MZRAN, RngInitModeEnum.INIT_DEFAULT)
    m.randomInit( rng )

    with pytest.raises(ValueError):
        m.copyColumn(0,2)

    with pytest.raises(ValueError):
        m.copyColumn(2,0)

    with pytest.raises(ValueError):
        m.copyColumn(-2,0)

    m.copyColumn(1, 0)
    for i in range(m.rows()):
        assert m[i, 0] == m[i, 1]


def test_matrix_scale():
    m = Matrix(2,2 , value = 1)
    m.scaleColumn(0 , 2)
    assert m[0, 0] == 2
    assert m[1, 0] == 2

    m.setAll(1)
    m.scaleRow(1 , 2 )
    assert m[1, 0] == 2
    assert m[1, 1] == 2

    with pytest.raises(IndexError):
        m.scaleColumn(10 , 99)

    with pytest.raises(IndexError):
        m.scaleRow(10 , 99)


def test_matrix_equality():
    m = Matrix(2, 2)
    m[0, 0] = 2
    m[1, 1] = 4

    s = Matrix(2, 3)
    s[0, 0] = 2
    s[1, 1] = 4
    assert m != s

    r = Matrix(2, 2)
    r[0, 0] = 2
    r[1, 1] = 3
    assert m != r

    r[1, 1] = 4
    assert m == r


def test_str(tmpdir):
    m = Matrix(2, 2)
    s = str(m)

    m[0,0] = 0
    m[0,1] = 1
    m[1,0] = 2
    m[1,1] = 3

    with tmpdir.as_cwd():
        with copen("matrix.txt", "w") as f:
            m.fprint( f )

        with open("matrix.txt") as f:
            l1 = map(float, f.readline().split())
            l2 = map(float, f.readline().split())

        assert l1[0] == m[0, 0]
        assert l1[1] == m[0, 1]
        assert l2[0] == m[1, 0]
        assert l2[1] == m[1, 1]


def test_copy_equal():
    m1 = Matrix(2, 2)
    m1[0,0] = 0
    m1[0,1] = 1
    m1[1,0] = 2
    m1[1,1] = 3

    m2 = m1.copy( )
    assert m1 == m2


def test_sub_copy():
    m1 = Matrix(3,3)
    rng = RandomNumberGenerator(RngAlgTypeEnum.MZRAN, RngInitModeEnum.INIT_DEFAULT)
    m1.randomInit( rng )

    with pytest.raises(ValueError):
        m2 = m1.subCopy( 0,0,4,2 )

    with pytest.raises(ValueError):
        m2 = m1.subCopy( 0,0,2,4 )

    with pytest.raises(ValueError):
        m2 = m1.subCopy( 4,0,1,1 )

    with pytest.raises(ValueError):
        m2 = m1.subCopy( 0,2,1,2 )

    m2 = m1.subCopy( 0,0,2,2 )
    for i in range(2):
        for j in range(2):
            assert m1[i, j] == m2[i, j]


def test_transpose():
    m = Matrix(3,2)
    m[0,0] = 0
    m[1,0] = 2
    m[2,0] = 4

    m[0,1] = 1
    m[1,1] = 3
    m[2,1] = 5

    mt = m.transpose( )

    assert m[0,0] == 0
    assert m[1,0] == 2
    assert m[2,0] == 4

    assert m[0,1] == 1
    assert m[1,1] == 3
    assert m[2,1] == 5

    assert mt.rows() == m.columns()
    assert mt.columns() == m.rows()
    assert mt[0,0] == 0
    assert mt[1,0] == 1

    assert mt[0,1] == 2
    assert mt[1,1] == 3

    assert mt[0,2] == 4
    assert mt[1,2] == 5

    m.transpose( inplace = True )
    assert m == mt


def test_matmul():
    m1 = Matrix(3,3)
    m2 = Matrix(2,2)

    with pytest.raises(ValueError):
        Matrix.matmul( m1 , m2 )

    m = Matrix(3,2)
    m[0,0] = 0
    m[1,0] = 2
    m[2,0] = 4

    m[0,1] = 1
    m[1,1] = 3
    m[2,1] = 5

    mt = m.transpose( )

    m2 = Matrix.matmul( m , mt )

    assert m2[0,0] == 1
    assert m2[1,1] == 13
    assert m2[2,2] == 41


def test_csv(tmpdir):
    m = Matrix(2, 2)
    m[0, 0] = 2
    m[1, 1] = 4
    with tmpdir.as_cwd():
        m.dumpCSV("matrix.csv")


def test_identity():
    m1 = Matrix.identity(1)
    assert m1.rows() == 1
    assert m1.columns() == 1
    assert m1[0, 0] == 1

    with pytest.raises(ValueError):
        Matrix.identity(0)
    with pytest.raises(ValueError):
        Matrix.identity(-3)

    m = Matrix.identity(17)
    assert m.rows() == 17
    assert m.columns() == 17
    for i in range(17):
        for j in range(17):
            elt = m[i, j]
            if i == j:
                assert elt == 1
            else:
                assert elt == 0