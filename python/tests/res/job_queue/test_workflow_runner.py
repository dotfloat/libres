import os
import time
from res.job_queue import WorkflowJoblist, Workflow, WorkflowRunner
from tests import ResTest
from ecl.util.test import TestAreaContext
from res.util.substitution_list import SubstitutionList
from .workflow_common import WorkflowCommon


class WorkflowRunnerTest(ResTest):

    def test_workflow_thread_cancel_ert_script(self):
        with TestAreaContext("python/job_queue/workflow_runner_ert_script") as work_area:
            WorkflowCommon.createWaitJob()

            joblist = WorkflowJoblist()
            assert joblist.addJobFromFile("WAIT", "wait_job")
            assert "WAIT" in joblist

            workflow = Workflow("wait_workflow", joblist)

            assert len(workflow) == 3


            workflow_runner = WorkflowRunner(workflow)

            assert not workflow_runner.isRunning()

            workflow_runner.run()

            assert workflow_runner.workflowResult() is None

            time.sleep(1) # wait for workflow to start
            assert workflow_runner.isRunning()
            assert os.path.isfile("wait_started_0")

            time.sleep(1) # wait for first job to finish

            workflow_runner.cancel()
            time.sleep(1) # wait for cancel to take effect
            assert os.path.isfile("wait_finished_0")


            assert os.path.isfile("wait_started_1")
            assert os.path.isfile("wait_cancelled_1")
            assert not os.path.isfile("wait_finished_1")

            assert workflow_runner.isCancelled()

            workflow_runner.wait() # wait for runner to complete

            assert not os.path.isfile("wait_started_2")
            assert not os.path.isfile("wait_cancelled_2")
            assert not os.path.isfile("wait_finished_2")




    def test_workflow_thread_cancel_external(self):
        with TestAreaContext("python/job_queue/workflow_runner_external") as work_area:
            WorkflowCommon.createWaitJob()

            joblist = WorkflowJoblist()
            assert joblist.addJobFromFile("WAIT", "external_wait_job")
            assert "WAIT" in joblist

            workflow = Workflow("wait_workflow", joblist)

            assert len(workflow) == 3


            workflow_runner = WorkflowRunner(workflow, ert=None, context=SubstitutionList())

            assert not workflow_runner.isRunning()

            workflow_runner.run()

            time.sleep(1) # wait for workflow to start
            assert workflow_runner.isRunning()
            assert os.path.isfile("wait_started_0")

            time.sleep(1) # wait for first job to finish

            workflow_runner.cancel()
            time.sleep(1) # wait for cancel to take effect
            assert os.path.isfile("wait_finished_0")

            assert os.path.isfile("wait_started_1")
            assert not os.path.isfile("wait_finished_1")

            assert workflow_runner.isCancelled()

            workflow_runner.wait() # wait for runner to complete

            assert not os.path.isfile("wait_started_2")
            assert not os.path.isfile("wait_cancelled_2")
            assert not os.path.isfile("wait_finished_2")


    def test_workflow_success(self):
        with TestAreaContext("python/job_queue/workflow_runner_fast") as work_area:
            WorkflowCommon.createWaitJob()

            joblist = WorkflowJoblist()
            assert joblist.addJobFromFile("WAIT", "wait_job")
            assert joblist.addJobFromFile("EXTERNAL_WAIT", "external_wait_job")

            workflow = Workflow("fast_wait_workflow", joblist)

            assert len(workflow) == 2


            workflow_runner = WorkflowRunner(workflow, ert=None, context=SubstitutionList())

            assert not workflow_runner.isRunning()

            workflow_runner.run()
            time.sleep(1) # wait for workflow to start
            workflow_runner.wait()

            assert os.path.isfile("wait_started_0")
            assert not os.path.isfile("wait_cancelled_0")
            assert os.path.isfile("wait_finished_0")

            assert os.path.isfile("wait_started_1")
            assert not os.path.isfile("wait_cancelled_1")
            assert os.path.isfile("wait_finished_1")

            assert workflow_runner.workflowResult()