import os.path
import random
from tests import ResTest
from ecl.util.test import TestRun , path_exists



class RunTest(ResTest):
    def setUp(self):
        # Slightly weird - tests need existing file,
        # but it can be empty ....
        self.testConfig = "/tmp/config-%06d" % random.randint( 100000 , 999999 )
        with open(self.testConfig , "w") as f:
            pass


    def test_init(self):
        with pytest.raises(IOError):
            TestRun("Does/notExist")

        tr = TestRun(self.testConfig)
        assert tr.config_file == os.path.split( self.testConfig)[1]
        assert tr.ert_version == "stable"


    def test_args(self):
        tr = TestRun(self.testConfig , args=["-v" , "latest"])
        assert tr.ert_version == "latest"


    def test_cmd(self):
        tr = TestRun(self.testConfig)
        assert tr.ert_cmd == TestRun.default_ert_cmd

        tr.ert_cmd = "/tmp/test"
        assert "/tmp/test" == tr.ert_cmd


    def test_args2(self):
        tr = TestRun(self.testConfig , args = ["arg1","arg2","-v","latest"])
        assert tr.get_args() == ["arg1","arg2"]
        assert tr.ert_version == "latest"


    def test_workflows(self):
        tr = TestRun(self.testConfig)
        assert tr.get_workflows() == []

        tr.add_workflow( "wf1" )
        tr.add_workflow( "wf2" )
        assert tr.get_workflows() == ["wf1" , "wf2"]


    def test_run_no_workflow(self):
        tr = TestRun(self.testConfig)
        with pytest.raises(Exception):
            tr.run()




    def test_runpath(self):
        tr = TestRun(self.testConfig , "Name")
        assert TestRun.default_path_prefix == tr.path_prefix


    def test_check(self):
        tr = TestRun(self.testConfig , "Name")
        tr.add_check( path_exists , "some/file" )

        with pytest.raises(Exception):
            tr.add_check( 25 , "arg")

        with pytest.raises(Exception):
            tr.add_check( func_does_not_exist , "arg")