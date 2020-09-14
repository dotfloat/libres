import ecl
import res.enkf  # noqa

from res.job_queue import WorkflowJob
from tests import ResTest
from ecl.util.test import TestAreaContext
from .workflow_common import WorkflowCommon

from cwrap import Prototype

class _TestWorkflowJobPrototype(Prototype):
    lib = res.load('libres')

    def __init__(self, prototype, bind=True):
        super(_TestWorkflowJobPrototype, self).__init__(_TestWorkflowJobPrototype.lib, prototype, bind=bind)

class WorkflowJobTest(ResTest):
    _alloc_config    = _TestWorkflowJobPrototype("void* workflow_job_alloc_config()", bind = False)
    _alloc_from_file = _TestWorkflowJobPrototype("workflow_job_obj workflow_job_config_alloc(char*, void*, char*)", bind = False)


    def test_workflow_job_creation(self):
        workflow_job = WorkflowJob("Test")

        assert workflow_job.isInternal()
        assert workflow_job.name() == "Test"


    def test_read_internal_function(self):
        with TestAreaContext("python/job_queue/workflow_job") as work_area:
            WorkflowCommon.createInternalFunctionJob()
            WorkflowCommon.createErtScriptsJob()

            config = self._alloc_config()
            workflow_job = self._alloc_from_file("SELECT_CASE", config, "select_case_job")

            assert workflow_job.name() == "SELECT_CASE"
            assert workflow_job.isInternal()
            assert workflow_job.functionName() == "enkf_main_select_case_JOB"

            assert not workflow_job.isInternalScript()
            assert workflow_job.getInternalScriptPath() is None


            workflow_job = self._alloc_from_file("SUBTRACT", config, "subtract_script_job")
            assert workflow_job.name() == "SUBTRACT"
            assert workflow_job.isInternal()
            assert workflow_job.functionName() is None

            assert workflow_job.isInternalScript()
            assert workflow_job.getInternalScriptPath().endswith("subtract_script.py")



    def test_arguments(self):
        with TestAreaContext("python/job_queue/workflow_job") as work_area:
            WorkflowCommon.createInternalFunctionJob()

            config = self._alloc_config()
            job = self._alloc_from_file("PRINTF", config, "printf_job")

            assert job.minimumArgumentCount() == 4
            assert job.maximumArgumentCount() == 5
            assert job.argumentTypes() == [str, int, float, bool, str]

            assert job.run(None, ["x %d %f %d", 1, 2.5, True])
            assert job.run(None, ["x %d %f %d %s", 1, 2.5, True, "y"])

            with self.assertRaises(UserWarning): # Too few arguments
                job.run(None, ["x %d %f", 1, 2.5])

            with self.assertRaises(UserWarning): # Too many arguments
                job.run(None, ["x %d %f %d %s", 1, 2.5, True, "y", "nada"])


    def test_run_external_job(self):

        with TestAreaContext("python/job_queue/workflow_job") as work_area:
            WorkflowCommon.createExternalDumpJob()

            config = self._alloc_config()
            job = self._alloc_from_file("DUMP", config, "dump_job")

            assert not job.isInternal()
            argTypes = job.argumentTypes()
            assert argTypes == [str , str]
            assert job.run(None, ["test", "text"]) is None
            assert job.stdoutdata() == "Hello World\n"

            with open("test", "r") as f:
                assert f.read() == "text"

    def test_error_handling_external_job(self):

        with TestAreaContext("python/job_queue/workflow_job") as work_area:
            WorkflowCommon.createExternalDumpJob()

            config = self._alloc_config()
            job = self._alloc_from_file("DUMP", config, "dump_failing_job")

            assert not job.isInternal()
            argTypes = job.argumentTypes()
            assert job.run(None, []) is None
            assert job.stderrdata().startswith('Traceback')


    def test_run_internal_script(self):
        with TestAreaContext("python/job_queue/workflow_job") as work_area:
            WorkflowCommon.createErtScriptsJob()

            config = self._alloc_config()
            job = self._alloc_from_file("SUBTRACT", config, "subtract_script_job")

            result = job.run(None, ["1", "2"])

            assert result == -1
