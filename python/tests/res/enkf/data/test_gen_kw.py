import os.path
from res.enkf.data import GenKw
from res.enkf.config import GenKwConfig
from tests import ResTest
from tests.utils import tmpdir


def create_gen_kw():
    parameter_file ="MULTFLT.txt"
    template_file ="MULTFLT.tmpl"
    with open(parameter_file, "w") as f:
        f.write("MULTFLT1  NORMAL  0   1\n")
        f.write("MULTFLT2  RAW \n")
        f.write("MULTFLT3  NORMAL  0   1\n")

    with open(template_file, "w") as f:
        f.write("<MULTFLT1> <MULTFLT2> <MULTFLT3>\n")
        f.write("/\n")


    gen_kw_config = GenKwConfig("MULTFLT", template_file , parameter_file)
    gen_kw = GenKw( gen_kw_config )

    return (gen_kw_config , gen_kw)



class GenKwTest(ResTest):
    @tmpdir()
    def test_gen_kw_get_set(self):
        (gen_kw_config , gen_kw) = create_gen_kw()
        assert isinstance(gen_kw, GenKw)

        gen_kw[0] = 3.0
        assert gen_kw[0] == 3.0

        gen_kw["MULTFLT1"] = 4.0
        assert gen_kw["MULTFLT1"] == 4.0
        assert gen_kw[0] == 4.0

        gen_kw["MULTFLT2"] = 8.0
        assert gen_kw["MULTFLT2"] == 8.0
        assert gen_kw[1] == 8.0

        gen_kw["MULTFLT3"] = 12.0
        assert gen_kw["MULTFLT3"] == 12.0
        assert gen_kw[2] == 12.0

        assert len(gen_kw) == 3

        with pytest.raises(IndexError):
            gen_kw[4]

        with pytest.raises(TypeError):
            gen_kw[1.5]

        with pytest.raises(KeyError):
            gen_kw["MULTFLT_2"]

        assert "MULTFLT1" in gen_kw 

        items = gen_kw.items()
        assert len(items) == 3
        assert items[0][0] == "MULTFLT1"
        assert items[1][0] == "MULTFLT2"
        assert items[2][0] == "MULTFLT3"

        assert items[0][1] == 4
        assert items[1][1] == 8
        assert items[2][1] == 12

    @tmpdir()
    def test_gen_kw_get_set_vector(self):
        (gen_kw_config , gen_kw) = create_gen_kw()
        with pytest.raises(ValueError):
            gen_kw.setValues([0])

        with pytest.raises(TypeError):
            gen_kw.setValues(["A","B","C"])

        gen_kw.setValues([0,1,2])
        assert gen_kw[0] == 0
        assert gen_kw[1] == 1
        assert gen_kw[2] == 2

        assert gen_kw["MULTFLT1"] == 0
        assert gen_kw["MULTFLT2"] == 1
        assert gen_kw["MULTFLT3"] == 2

    @tmpdir()
    def test_gen_kw_ecl_write(self):
        (gen_kw_config , gen_kw) = create_gen_kw()

        with pytest.raises(IOError):
            gen_kw.eclWrite( "tmp" , "file.txt")

        gen_kw.eclWrite( None , "file.txt")
        assert  os.path.isfile( "file.txt" )

        os.mkdir("tmp")
        gen_kw.eclWrite( "tmp" , "file.txt")
        assert  os.path.isfile( "tmp/file.txt" )

        gen_kw.exportParameters( "tmp/export.txt" )
        assert  os.path.isfile( "tmp/export.txt" )