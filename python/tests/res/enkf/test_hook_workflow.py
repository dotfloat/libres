from res.enkf.enums import HookRuntime
from tests import ResTest


class HookWorkFlowTest(ResTest):

    def test_enum(self):
        res_helper.assert_enum_fully_defined(HookRuntime, "hook_run_mode_enum" , "lib/include/ert/enkf/hook_workflow.hpp", verbose=True)
