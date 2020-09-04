import os
import os.path
import pytest

from job_runner.job import Job
from job_runner.reporting import File
from job_runner.reporting.message import Exited, Finish, Init, Running, Start


@pytest.fixture(scope="module")
def reporter():
    return File()


def test_report_with_init_message_argument(tmpdir, reporter):
    with tmpdir.as_cwd():
        r = reporter
        job1 = Job({"name": "job1", "stdout": "/stdout", "stderr": "/stderr"}, 0)

        r.report(Init([job1], 1, 19))

        with open(self.reporter.STATUS_file, "r") as f:
            assert "Current host" in f.readline()

        with open(self.reporter.STATUS_json, "r") as f:
            contents = "".join(f.readlines())
            assert '"name": "job1"' in contents
            assert '"status": "Waiting"' in contents


def test_report_with_successful_start_message_argument(tmpdir, reporter):
    with tmpdir.as_cwd():
        msg = Start(
            Job(
                {
                    "name": "job1",
                    "stdout": "/stdout",
                    "stderr": "/stderr",
                    "argList": ["--foo", "1", "--bar", "2"],
                    "executable": "/bin/bash",
                },
                0,
            )
        )
        reporter.status_dict = reporter._init_job_status_dict(
            msg.timestamp, 0, [msg.job]
        )

        reporter.report(msg)

        with open(reporter.STATUS_file) as f:
            assert "job1" in f.readline()

        with open(reporter.LOG_file) as f:
            assert "Calling: /bin/bash --foo 1 --bar 2" in f.readline()

        with open(reporter.STATUS_json) as f:
            contents = "".join(f.readlines())
            assert '"status": "Running"' in contents
            assert '"start_time": null' not in contents


def test_report_with_failed_start_message_argument(tmpdir, reporter):
    with tmpdir.as_cwd():
        msg = Start(Job({"name": "job1"}, 0)).with_error("massive_failure")
        reporter.status_dict = reporter._init_job_status_dict(
            msg.timestamp, 0, [msg.job]
        )

        reporter.report(msg)

        with open(reporter.STATUS_file) as f:
            "EXIT: -10/massive_failure" in f.readline()

        with open(reporter.STATUS_json) as f:
            contents = "".join(f.readlines())
            assert '"status": "Failure"' in contents
            assert '"error": "massive_failure"' in contents

        assert reporter.status_dict["jobs"][0]["end_time"] is not None


def test_report_with_successful_exit_message_argument(tmpdir, reporter):
    with tmpdir.as_cwd():
        msg = Exited(Job({"name": "job1"}, 0), 0)
        reporter.status_dict = reporter._init_job_status_dict(
            msg.timestamp, 0, [msg.job]
        )

        reporter.report(msg)

        with open(reporter.STATUS_json) as f:
            contents = "".join(f.readlines())
            assert '"status": "Success"' in contents


def test_report_with_failed_exit_message_argument(tmpdir, reporter):
    with tmpdir.as_cwd():
        msg = Exited(Job({"name": "job1"}, 0), 1).with_error("massive_failure")
        reporter.status_dict = reporter._init_job_status_dict(
            msg.timestamp, 0, [msg.job]
        )

        reporter.report(msg)

        with open(reporter.STATUS_file) as f:
            assert "EXIT: 1/massive_failure" in f.readline()

        with open(reporter.ERROR_file) as f:
            contents = "".join(f.readlines())
            assert "<job>job1</job>" in contents
            assert "<reason>massive_failure</reason>" in contents
            assert "<stderr: Not redirected>" in contents

        with open(reporter.STATUS_json) as f:
            contents = "".join(f.readlines())
            assert '"status": "Failure"' in contents
            assert '"error": "massive_failure"' in contents

        assert self.reporter.status_dict["jobs"][0]["end_time"] is not None


def test_report_with_running_message_argument(tmpdir, reporter):
    with tmpdir.as_cwd():
        msg = Running(Job({"name": "job1"}, 0), 100, 10)
        reporter.status_dict = reporter._init_job_status_dict(
            msg.timestamp, 0, [msg.job]
        )

        reporter.report(msg)

        with open(reporter.STATUS_json) as f:
            contents = "".join(f.readlines())
            assert '"status": "Running"' in contents
            assert '"max_memory_usage": 100' in contents
            assert '"current_memory_usage": 10' in contents


def test_report_with_successful_finish_message_argument(tmpdir, reporter):
    with tmpdir.as_cwd():
        msg = Finish()
        reporter.status_dict = reporter._init_job_status_dict(
            msg.timestamp, 0, []
        )

        reporter.report(msg, sync_disc_timeout=0)

        with open(reporter.OK_file) as f:
            assert "All jobs complete" in f.readline()


def test_dump_error_file_with_stderr(tmpdir, reporter):
    """
    Assert that, in the case of an stderr file, it is included in the XML
    that constitutes the ERROR file.
    The report system is left out, since this was tested in the fail case.
    """
    with tmpdir.as_cwd():
        with open("stderr.out.0", "a") as stderr:
            stderr.write("Error:\n")
            stderr.write("E_MASSIVE_FAILURE\n")

        reporter._dump_error_file(
            Job({"name": "job1", "stderr": "stderr.out"}, 0), "massive_failure"
        )

        with open(reporter.ERROR_file) as f:
            contents = "".join(f.readlines())
            assert "E_MASSIVE_FAILURE" in contents
            assert "<stderr_file>" in contents


def test_old_file_deletion(tmpdir, reporter):
    with tmpdir.as_cwd():
        r = reporter
        # touch all files that are to be removed
        for f in [r.EXIT_file, r.ERROR_file, r.STATUS_file, r.OK_file]:
            open(f, "a").close()

        r._delete_old_status_files()

        for f in [r.EXIT_file, r.ERROR_file, r.STATUS_file, r.OK_file]:
            assert not os.path.isfile(f)


def test_status_file_is_correct(tmpdir, reporter):
    """The STATUS file is a file to which we append data about jobs as they
    are run. So this involves multiple reports, and should be tested as
    such.
    See https://github.com/equinor/libres/issues/764
    """
    with tmpdir.as_cwd():
        j_1 = Job({"name": "j_1", "executable": "", "argList": []}, 0)
        j_2 = Job({"name": "j_2", "executable": "", "argList": []}, 0)
        init = Init([j_1, j_2], 1, 1)
        start_j_1 = Start(j_1)
        exited_j_1 = Exited(j_1, 0)
        start_j_2 = Start(j_2)
        exited_j_2 = Exited(j_2, 9).with_error("failed horribly")

        for msg in [init, start_j_1, exited_j_1, start_j_2, exited_j_2]:
            reporter.report(msg)

        expected_j1_line = "{:32}: {start_ts:%H:%M:%S} .... {end_ts:%H:%M:%S}  \n".format(  # noqa
            j_1.name(), start_ts=start_j_1.timestamp, end_ts=exited_j_1.timestamp
        )
        expected_j2_line = "{:32}: {start_ts:%H:%M:%S} .... {end_ts:%H:%M:%S}   EXIT: {code}/{msg}\n".format(  # noqa
            j_2.name(),
            start_ts=start_j_2.timestamp,
            end_ts=exited_j_2.timestamp,
            code=exited_j_2.exit_code,
            msg=exited_j_2.error_message,
        )

        with open(reporter.STATUS_file) as f:
            for expected in [
                "Current host",
                expected_j1_line,
                expected_j2_line,
            ]:  # noqa
                assert expected in f.readline()

            # EOF
            assert f.readline() == ""
