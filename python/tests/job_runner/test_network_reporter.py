import sys
import pytest
from datetime import datetime as dt

from job_runner.job import Job
from job_runner.reporting import Network
from job_runner.reporting.message import Exited, Init, Finish


@pytest.fixture(scope="module")
def reporter():
    return Network()


def test_init_msg(reporter, mocker):
    post_mock = mocker.patch("job_runner.reporting.network.requests.post")
    reporter.report(Init([], 0, 1))
    assert post_mock.called


def test_failed_job_is_reported(reporter, mocker):
    post_mock = mocker.patch("job_runner.reporting.network.requests.post")
    reporter.start_time = dt.now()
    job = Job({"name": "failing job", "executable": "/dev/null", "argList": []}, 0)

    reporter.report(Exited(job, 9).with_error("failed"))
    _, data = post_mock.call_args

    assert post_mock.called
    assert '"status": "exit"' in data["data"]
    assert '"error": true' in data["data"]


def test_successful_job_not_reported(reporter, mocker):
    post_mock = mocker.patch("job_runner.reporting.network.requests.post")
    reporter.report(Exited(None, 9))
    assert not post_mock.called


def test_successful_forward_model_reported(reporter, mocker):
    post_mock = mocker.patch("job_runner.reporting.network.requests.post")
    reporter.start_time = dt.now()

    reporter.report(Finish())
    _, data = post_mock.call_args

    assert post_mock.called
    assert '"status": "OK"' in data["data"]


def test_failed_forward_model_not_reported(reporter, mocker):
    post_mock = mocker.patch("job_runner.reporting.network.requests.post")
    reporter.report(Finish().with_error("failed"))
    assert not post_mock.called
