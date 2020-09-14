from res.enkf import SummaryKeyMatcher
from tests import ResTest

class SummaryKeyMatcherTest(ResTest):

    def test_creation(self):
        matcher = SummaryKeyMatcher()

        assert len(matcher) == 0

        matcher.addSummaryKey("F*")
        assert len(matcher) == 1

        matcher.addSummaryKey("F*")
        assert len(matcher) == 1

        matcher.addSummaryKey("FOPT")
        assert len(matcher) == 2

        assert set(["F*", "FOPT"]) == set(matcher.keys())

        assert "FGIR" in matcher
        assert "FOPT" in matcher
        assert not "TCPU" in matcher

        assert matcher.isRequired("FOPT")
        assert not matcher.isRequired("FGIR")
        assert not matcher.isRequired("TCPU")