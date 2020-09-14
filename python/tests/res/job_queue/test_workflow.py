from res.job_queue import Workflow, WorkflowJoblist
from ecl.util.test import TestAreaContext
from tests import ResTest
from res.util.substitution_list import SubstitutionList
from .workflow_common import WorkflowCommon


class WorkflowTest(ResTest):

    def test_workflow(self):
        with TestAreaContext("python/job_queue/workflow") as work_area:
            WorkflowCommon.createExternalDumpJob()

            joblist = WorkflowJoblist()
            assert joblist.addJobFromFile("DUMP", "dump_job")

            with pytest.raises(UserWarning):
                joblist.addJobFromFile("KNOCK", "knock_job")

            assert "DUMP" in joblist


            workflow = Workflow("dump_workflow", joblist)

            assert len(workflow) == 2

            job, args = workflow[0]
            assert job == joblist["DUMP"]
            assert args[0] == "dump1"
            assert args[1] == "dump_text_1"

            job, args = workflow[1]
            assert job == joblist["DUMP"]


    def test_workflow_run(self):
        with TestAreaContext("python/job_queue/workflow") as work_area:
            WorkflowCommon.createExternalDumpJob()

            joblist = WorkflowJoblist()
            assert joblist.addJobFromFile("DUMP", "dump_job")
            assert "DUMP" in joblist

            workflow = Workflow("dump_workflow", joblist)

            assert len(workflow), 2

            context = SubstitutionList()
            context.addItem("<PARAM>", "text")

            assert workflow.run(None, verbose=True, context=context)

            with open("dump1", "r") as f:
                assert f.read() == "dump_text_1"

            with open("dump2", "r") as f:
                assert f.read() == "dump_text_2"


    def test_failing_workflow_run(self):
        with TestAreaContext("python/job_queue/workflow") as work_area:
            WorkflowCommon.createExternalDumpJob()

            joblist = WorkflowJoblist()
            assert joblist.addJobFromFile("DUMP", "dump_job")
            assert "DUMP" in joblist

            workflow = Workflow("undefined", joblist)
            context = SubstitutionList()

            assert not workflow.run(None, verbose=True, context=context)