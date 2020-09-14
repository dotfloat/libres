import pytest
import ctypes
from res import ResPrototype
from res.util import CThreadPool, startCThreadPool

TEST_LIB = ResPrototype.lib


def test_cfunc():
    with pytest.raises(TypeError):
        func = CThreadPool.lookupCFunction("WRONG-TYPE", "no-this-does-not-exist")

    with pytest.raises(AttributeError):
        func = CThreadPool.lookupCFunction(TEST_LIB, "no-this-does-not-exist")


def test_create():
    pool = CThreadPool(32, start=True)
    job = CThreadPool.lookupCFunction(TEST_LIB, "thread_pool_test_func1")
    arg = ctypes.c_int(0)

    N = 256
    for i in range(N):
        pool.addTask(job, ctypes.byref(arg))
    pool.join()
    assert arg.value == N


def test_context():
    N = 256
    arg = ctypes.c_int(0)
    job = CThreadPool.lookupCFunction(TEST_LIB, "thread_pool_test_func1")
    with startCThreadPool(16) as tp:
        for i in range(N):
            tp.addTask(job, ctypes.byref(arg))
    assert arg.value == N


def test_add_task_function():
    pool = CThreadPool(32, start=True)
    pool.addTaskFunction("testFunction", TEST_LIB, "thread_pool_test_func1")

    arg = ctypes.c_int(0)
    task_count = 256
    for i in range(task_count):
        pool.testFunction(ctypes.byref(arg))

    pool.join()
    assert arg.value == task_count