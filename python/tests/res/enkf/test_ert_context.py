from tests import ResTest
import sys

from res.test import ErtTestContext
import pytest

import os

@pytest.mark.equinor_test
class ErtTestContextTest(ResTest):
    def setUp(self):
        self.config = self.createTestPath("Equinor/config/with_data/config")

    def test_raises(self):
        with pytest.raises(IOError):
            testContext = ErtTestContext("ExistTest" , "Does/not/exist")


    def initFromCaseTest(self, context, root_path):
        ert = context.getErt()

        init_case_job = self.createSharePath("%s/INIT_CASE_FROM_EXISTING" % root_path)
        context.installWorkflowJob("INIT_CASE_JOB", init_case_job)
        assert context.runWorkflowJob("INIT_CASE_JOB", "default", "new_not_current_case")

        default_fs = ert.getEnkfFsManager().getFileSystem("default")
        new_fs = ert.getEnkfFsManager().getFileSystem("new_not_current_case")

        assert default_fs is not None
        assert new_fs is not None

        assert len(default_fs.getStateMap()) > 0
        assert len(default_fs.getStateMap()) == len(new_fs.getStateMap())


    def createCaseTest(self, context, root_path):
        create_case_job = self.createSharePath("%s/CREATE_CASE" % root_path)
        context.installWorkflowJob("CREATE_CASE_JOB", create_case_job)
        assert context.runWorkflowJob("CREATE_CASE_JOB", "newly_created_case")
        assert os.path.isdir("storage/newly_created_case")


    def selectCaseTest(self, context, root_path):
        ert = context.getErt()
        select_case_job = self.createSharePath("%s/SELECT_CASE" % root_path)

        default_fs = ert.getEnkfFsManager().getCurrentFileSystem()

        custom_fs = ert.getEnkfFsManager().getFileSystem("CustomCase")

        assert ert.getEnkfFsManager().getCurrentFileSystem() == default_fs

        context.installWorkflowJob("SELECT_CASE_JOB", select_case_job)
        assert context.runWorkflowJob("SELECT_CASE_JOB", "CustomCase")

        assert ert.getEnkfFsManager().getCurrentFileSystem() == custom_fs


    def loadResultsTest(self, context):
        load_results_job = self.createSharePath("ert/workflows/jobs/internal/config/LOAD_RESULTS")
        context.installWorkflowJob("LOAD_RESULTS_JOB", load_results_job)
        assert context.runWorkflowJob("LOAD_RESULTS_JOB", 0, 1)


    def rankRealizationsOnObservationsTest(self, context):
        rank_job = self.createSharePath("ert/workflows/jobs/internal/config/OBSERVATION_RANKING")

        context.installWorkflowJob("OBS_RANK_JOB", rank_job)

        assert context.runWorkflowJob("OBS_RANK_JOB", "NameOfObsRanking1", "|", "WOPR:*")
        assert context.runWorkflowJob("OBS_RANK_JOB", "NameOfObsRanking2", "1-5", "55", "|", "WWCT:*", "WOPR:*")
        assert context.runWorkflowJob("OBS_RANK_JOB", "NameOfObsRanking3", "5", "55", "|")
        assert context.runWorkflowJob("OBS_RANK_JOB", "NameOfObsRanking4", "1,3,5-10", "55")
        assert context.runWorkflowJob("OBS_RANK_JOB", "NameOfObsRanking5")
        assert context.runWorkflowJob("OBS_RANK_JOB", "NameOfObsRanking6", "|", "UnrecognizableObservation")


    def test_workflow_function_jobs(self):

        with ErtTestContext("python/enkf/ert_test_context_workflow_function_job", self.config) as context:
            internal_config = "ert/workflows/jobs/internal-tui/config"
            self.createCaseTest(context, root_path=internal_config)
            self.selectCaseTest(context, root_path=internal_config)

            # Due to EnKFFs caching and unmonitored C functions this will fail
            #self.initFromCaseTest(context, root_path=internal_config)

            self.loadResultsTest(context)
            self.rankRealizationsOnObservationsTest(context)



    def test_workflow_ert_script_jobs(self):

        with ErtTestContext("python/enkf/ert_test_context_workflow_ert_script_job", self.config) as context:
            with pytest.raises(IOError):
                context.installWorkflowJob("JOB_NAME" , "DOES/NOT/EXIST")

            ert_scripts_config = "ert/workflows/jobs/internal-gui/config"
            self.createCaseTest(context, root_path=ert_scripts_config)
            self.selectCaseTest(context, root_path=ert_scripts_config)
            self.initFromCaseTest(context, root_path=ert_scripts_config)

