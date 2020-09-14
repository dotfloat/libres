import os.path
import json
import pytest

from res.enkf.data import Summary
from res.enkf.config import SummaryConfig


def test_create():
    config = SummaryConfig("WWCT:OP_5")
    summary = Summary(config)
    assert len(summary) == 0

    with pytest.raises(IndexError):
        v = summary[100]
