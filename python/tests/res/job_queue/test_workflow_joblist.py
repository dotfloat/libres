import res.enkf  # noqa
from res.job_queue import WorkflowJoblist, WorkflowJob
from ecl.util.test import TestAreaContext
from tests import ResTest
from .workflow_common import WorkflowCommon


class WorkflowJoblistTest(ResTest):

    def test_workflow_joblist_creation(self):
        joblist = WorkflowJoblist()

        job = WorkflowJob("JOB1")

        joblist.addJob(job)

        assert job in joblist
        assert "JOB1" in joblist

        job_ref = joblist["JOB1"]

        assert job.name() == job_ref.name()



    def test_workflow_joblist_with_files(self):
        with TestAreaContext("python/job_queue/workflow_joblist") as work_area:
            WorkflowCommon.createErtScriptsJob()
            WorkflowCommon.createExternalDumpJob()
            WorkflowCommon.createInternalFunctionJob()

            joblist = WorkflowJoblist()

            joblist.addJobFromFile("DUMP_JOB", "dump_job")
            joblist.addJobFromFile("SELECT_CASE_JOB", "select_case_job")
            joblist.addJobFromFile("SUBTRACT_SCRIPT_JOB", "subtract_script_job")

            assert "DUMP_JOB" in joblist
            assert "SELECT_CASE_JOB" in joblist
            assert "SUBTRACT_SCRIPT_JOB" in joblist

            assert not (joblist["DUMP_JOB"]).isInternal()
            assert (joblist["SELECT_CASE_JOB"]).isInternal()
            assert (joblist["SUBTRACT_SCRIPT_JOB"]).isInternal()