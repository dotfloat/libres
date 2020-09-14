from tests import ResTest
from res.enkf import ForwardLoadContext

class ForwardLoadContextTest(ResTest):

    def test_create(self):
        ctx = ForwardLoadContext( report_step = 1 )
        assert 1 == ctx.getLoadStep( )
        