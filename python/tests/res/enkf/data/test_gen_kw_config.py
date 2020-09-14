from tests import ResTest
from tests.utils import tmpdir

from res.test import ErtTestContext
from res.enkf import ErtImplType, GenKwConfig

class GenKwConfigTest(ResTest):
    @tmpdir()
    def test_gen_kw_config(self):
        with open("template.txt","w") as f:
            f.write("Hello")

        with open("parameters.txt","w") as f:
            f.write("KEY  UNIFORM 0 1 \n")

        with open("parameters_with_comments.txt","w") as f:
            f.write("KEY1  UNIFORM 0 1 -- COMMENT\n")
            f.write("\n\n") # Two blank lines
            f.write("KEY2  UNIFORM 0 1\n")
            f.write("--KEY3  \n")
            f.write("KEY3  UNIFORM 0 1\n")

        template_file = "template.txt"
        parameter_file = "parameters.txt"
        parameter_file_comments = "parameters_with_comments.txt"
        with pytest.raises(IOError):
            conf = GenKwConfig("KEY", template_file, "does_not_exist")

        with pytest.raises(IOError):
            conf = GenKwConfig("Key", "does_not_exist", parameter_file)

        conf = GenKwConfig("KEY", template_file, parameter_file)
        conf = GenKwConfig("KEY", template_file, parameter_file_comments)
        assert len(conf) == 3