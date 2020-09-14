import pytest
import os
from res.util import ResLog, Log
from res.util.enums import MessageLevelEnum


def test_log(tmpdir):
    with tmpdir.as_cwd():
        test_log_filename = "test_log"
        ResLog.init(1, test_log_filename, True)
        message = "This is fun"
        ResLog.log(1, message)

        assert os.path.isfile(test_log_filename)

        with open(test_log_filename) as f:
            text = f.readlines()
            assert len(text) > 0
            assert message in text[-1]


def test_getFilename(tmpdir):
    with tmpdir.as_cwd():
        test_log_filename = "log_test_file.txt"
        ResLog.init(1, test_log_filename, True)
        message = "This is fun"
        ResLog.log(1, message)

        assert ResLog.getFilename() == test_log_filename


def test_log(tmpdir):
    with tmpdir.as_cwd():
        logh = Log("logfile", MessageLevelEnum.LOG_DEBUG)

        os.mkdir("read_only")
        os.chmod("read_only", 0o500)
        with pytest.raises(IOError):
            logh = Log("read_only/logfile.txt", MessageLevelEnum.LOG_DEBUG)


def test_init_perm_denied(tmpdir):
    with tmpdir.as_cwd():
        os.mkdir("read_only")
        os.chmod("read_only", 0o500)
        with pytest.raises(IOError):
            ResLog.init(1, "read_only/logfile.txt", True)
