from cwrap import clib
from ecl.util.test import TestAreaContext
from res.job_queue import WorkflowJob
from .workflow_common import WorkflowCommon
from tests import ResTest

class FunctionErtScriptTest(ResTest):

    def test_compare(self):
        with TestAreaContext("python/job_queue/workflow_job") as work_area:
            WorkflowCommon.createInternalFunctionJob()

            parser = WorkflowJob.configParser( )
            with pytest.raises(IOError):
                workflow_job = WorkflowJob.fromFile("no/such/file")

            workflow_job = WorkflowJob.fromFile("compare_job", name = "COMPARE", parser = parser)
            assert workflow_job.name() == "COMPARE"

            result = workflow_job.run(None , ["String", "string"])
            assert result != 0

            result = workflow_job.run(None, ["String", "String"])
            # result is returned as c_void_p -> automatic conversion to None if value is 0
            assert result is None

            workflow_job = WorkflowJob.fromFile("compare_job")
            assert workflow_job.name() == "compare_job"