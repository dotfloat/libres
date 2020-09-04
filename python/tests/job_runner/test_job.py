import os
import sys
import pytest

from job_runner.reporting.message import Exited, Running, Start
from job_runner.job import Job


def test_run_with_process_failing(tmpdir, mocker):
    with tmpdir.as_cwd():
        mock_process = mocker.patch("job_runner.job.assert_file_executable")
        mocker.patch("job_runner.job.Popen")
        mocker.patch("job_runner.job.Process")

        job = Job({}, 0)
        type(mock_process.return_value.memory_info.return_value).rss = mocker.PropertyMock(
            return_value=10
            )
        mock_process.return_value.wait.return_value = 9

        run = job.run()

        assert isinstance(next(run), Start)
        assert isinstance(next(run), Running)
        exited = next(run)
        print(mock_process().memory_info())
        assert isinstance(exited, Exited)
        assert int(exited.exit_code) == 9

        with pytest.raises(StopIteration):
            next(run)


def test_run_fails_using_exit_bash_builtin(tmpdir):
    with tmpdir.as_cwd():
        job = Job(
            {
                "name": "exit 1",
                "executable": "/bin/bash",
                "stdout": "exit_out",
                "stderr": "exit_err",
                "argList": ["-c", 'echo "failed with {}" 1>&2 ; exit {}'.format(1, 1)],
            },
            0,
            )

        statuses = list(job.run())

        assert len(statuses) == 3
        assert statuses[2].exit_code == 1
        assert statuses[2].error_message == "Process exited with status code 1"


def test_run_with_defined_executable_but_missing(tmpdir):
    with tmpdir.as_cwd():
        executable = str(tmpdir /  "this/is/not/a/file")
        job = Job(
            {
                "name": "TEST_EXECUTABLE_NOT_FOUND",
                "executable": executable,
                "stdout": "mkdir_out",
                "stderr": "mkdir_err",
            },
            0,
            )

        with pytest.raises(IOError):
            for _ in job.run():
                pass


def test_run_with_defined_executable_no_exec_bit(tmpdir):
    with tmpdir.as_cwd():
        non_executable = str(tmpdir / "foo")
        with open(non_executable, "a"):
            pass

        job = Job(
            {
                "name": "TEST_EXECUTABLE_NOT_EXECUTABLE",
                "executable": non_executable,
                "stdout": "mkdir_out",
                "stderr": "mkdir_err",
            },
            0,
            )

        with pytest.raises(IOError):
            for _ in job.run():
                pass
