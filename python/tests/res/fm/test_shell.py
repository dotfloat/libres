import unittest
import os
import os.path
import contextlib

from tests import ResTest
from tests.utils import tmpdir
from res.fm.shell import *
from _pytest.monkeypatch import MonkeyPatch

@contextlib.contextmanager
def pushd(path):
    cwd0 = os.getcwd()
    os.chdir(path)

    yield

    os.chdir(cwd0)


class ShellTest(ResTest):
    def setUp(self):
        self.monkeypatch = MonkeyPatch()


    def tearDown(self):
        self.monkeypatch.undo()

    @tmpdir()
    def test_symlink(self):
        with pytest.raises(IOError):
            symlink( "target/does/not/exist" , "link")

        with open("target", "w") as fileH:
            fileH.write("target ...")

        symlink( "target" , "link")
        assert  os.path.islink("link") 
        assert os.readlink("link") == "target"

        with open("target2", "w") as fileH:
            fileH.write("target ...")

        with pytest.raises(OSError):
            symlink("target2" , "target")


        symlink("target2" , "link")
        assert  os.path.islink("link") 
        assert os.readlink("link") == "target2"

        os.makedirs("root1/sub1/sub2")
        os.makedirs("root2/sub1/sub2")
        os.makedirs("run")

        symlink("../target" , "linkpath/link")
        assert  os.path.isdir( "linkpath" )
        assert  os.path.islink( "linkpath/link")

        symlink("../target" , "linkpath/link")
        assert  os.path.isdir( "linkpath" )
        assert  os.path.islink( "linkpath/link")

        os.makedirs("path")
        with open("path/target", "w") as f:
            f.write("1234")

        symlink("path/target" , "link")
        assert  os.path.islink( "link" )
        assert  os.path.isfile( "path/target" )

        symlink("path/target" , "link")
        assert  os.path.islink( "link" )
        assert  os.path.isfile( "path/target" )
        with open("link") as f:
            s = f.read( )
            assert s == "1234"

    @tmpdir()
    def test_mkdir(self):
        with open("file", "w") as f:
            f.write("Hei")

        with pytest.raises(OSError):
            mkdir( "file" )

        mkdir("path")
        assert  os.path.isdir( "path")
        mkdir("path")

        mkdir("path/subpath")
        assert  os.path.isdir( "path/subpath")

    @tmpdir()
    def test_move_file(self):
        with open("file", "w") as f:
            f.write("Hei")

        move_file("file" , "file2")
        assert  os.path.isfile("file2")
        assert not  os.path.isfile("file")

        with pytest.raises(IOError):
            move_file("file2" , "path/file2")

        mkdir("path")
        move_file("file2" , "path/file2")
        assert  os.path.isfile("path/file2")
        assert not  os.path.isfile( "file2") 

        with pytest.raises(IOError):
            move_file("path" , "path2")

        with pytest.raises(IOError):
            move_file("not_existing" , "target")

        with open("file2","w") as f:
            f.write("123")

        move_file("file2" , "path/file2")
        assert  os.path.isfile("path/file2")
        assert not  os.path.isfile( "file2") 

        mkdir("rms/ipl")
        with open("global_variables.ipl","w") as f:
            f.write("123")

        move_file("global_variables.ipl" , "rms/ipl/global_variables.ipl")

    @tmpdir()
    def test_move_file_into_folder_file_exists(self):
        mkdir("dst_folder")
        with open("dst_folder/file", "w") as f:
            f.write("old")

        with open("file", "w") as f:
            f.write("new")

        with open("dst_folder/file", "r") as f:
            content = f.read()
            assert content == "old"

        move_file("file", "dst_folder")
        with open("dst_folder/file", "r") as f:
            content = f.read()
            assert content == "new"

        assert not os.path.exists("file")

    @tmpdir()
    def test_move_pathfile_into_folder(self):
        mkdir("dst_folder")
        mkdir("source1/source2/")
        with open("source1/source2/file", "w") as f:
            f.write("stuff")

        move_file("source1/source2/file", "dst_folder")
        with open("dst_folder/file", "r") as f:
            content = f.read()
            assert content == "stuff"

        assert not os.path.exists("source1/source2/file")

    @tmpdir()
    def test_move_pathfile_into_folder_file_exists(self):
        mkdir("dst_folder")
        mkdir("source1/source2/")
        with open("source1/source2/file", "w") as f:
            f.write("stuff")

        with open("dst_folder/file", "w") as f:
            f.write("garbage")

        move_file("source1/source2/file", "dst_folder")
        with open("dst_folder/file", "r") as f:
            content = f.read()
            assert content == "stuff"

        assert not os.path.exists("source1/source2/file")

    @tmpdir()
    def test_delete_file(self):
        mkdir("pathx")
        with pytest.raises(IOError):
            delete_file( "pathx" )

        # deleteFile which does not exist - is silently ignored
        delete_file("does/not/exist")

        with open("file" , "w") as f:
            f.write("hei")
        symlink("file", "link")
        assert os.path.islink("link")

        delete_file("file")
        assert not  os.path.isfile( "file" )
        assert  os.path.islink("link")
        delete_file("link")
        assert not  os.path.islink("link")

    @tmpdir()
    def test_delete_directory(self):
        # deleteDriecteory which does not exist - is silently ignored
        delete_directory("does/not/exist")

        with open("file" , "w") as f:
            f.write("hei")

        with pytest.raises(IOError):
            delete_directory("file")

        mkdir("link_target/subpath")
        with open("link_target/link_file" , "w") as f:
            f.write("hei")

        mkdir("path/subpath")
        with open("path/file" , "w") as f:
            f.write("hei")

        with open("path/subpath/file" , "w") as f:
            f.write("hei")

        symlink( "../link_target" , "path/link")
        delete_directory("path")
        assert not  os.path.exists( "path" )
        assert  os.path.exists("link_target/link_file")

    @tmpdir()
    def test_copy_directory_error(self):
        with pytest.raises(IOError):
            copy_directory("does/not/exist" , "target")

        with open("file" , "w") as f:
            f.write("hei")

        with pytest.raises(IOError):
            copy_directory("hei" , "target")

    @tmpdir()
    def test_DATA_ROOT(self):
        mkdir("path/subpath")
        with open("path/subpath/file" , "w") as f:
            f.write("1")

        self.monkeypatch.setenv("DATA_ROOT", "path")
        mkdir("target/sub")
        copy_directory("subpath" , "target/sub")
        assert  os.path.exists( "target/sub/subpath" )
        assert  os.path.exists( "target/sub/subpath/file" )

        os.makedirs( "file_target")
        copy_file( "subpath/file" , "file_target")
        assert  os.path.isfile( "file_target/file" )

        copy_file( "subpath/file" , "subpath/file")
        with open("subpath/file") as f:
            v = int(f.read())
            assert v == 1

        with open("path/subpath/file" , "w") as f:
            f.write("2")
        copy_file( "subpath/file" , "subpath/file")
        with open("subpath/file") as f:
            v = int(f.read())
            assert v == 2

        symlink( "subpath/file" , "file_link")
        assert  os.path.isfile( "file_link" )
        assert  os.path.islink( "file_link" )
        assert os.readlink( "file_link" ) == "path/subpath/file"
        delete_directory( "subpath" )
        assert not  os.path.isdir( "path/subpath") 

    @tmpdir()
    def test_copy_file(self):
        with pytest.raises(IOError):
            copy_file("does/not/exist" , "target")

        mkdir("path")
        with pytest.raises(IOError):
            copy_file("path" , "target")


        with open("file1" , "w") as f:
            f.write("hei")

        copy_file("file1" , "file2")
        assert  os.path.isfile("file2") 

        copy_file("file1" , "path")
        assert  os.path.isfile("path/file1") 

        copy_file("file1" , "path2/file1")
        assert  os.path.isfile("path2/file1") 


        mkdir("root/sub/path")

        with open("file" , "w") as f:
            f.write("Hei ...")

        copy_file("file" , "root/sub/path/file")
        assert  os.path.isfile( "root/sub/path/file")

        with open("file2" , "w") as f:
            f.write("Hei ...")

        with pushd("root/sub/path"):
            copy_file("../../../file2")
            assert os.path.isfile("file2")

    @tmpdir()
    def test_copy_file2(self):
        mkdir("rms/output")

        with open("file.txt" , "w") as f:
            f.write("Hei")

        copy_file("file.txt" , "rms/output/")
        assert  os.path.isfile( "rms/output/file.txt" )

    @tmpdir()
    def test_careful_copy_file(self):
        with open("file1", "w") as f:
            f.write("hei")
        with open("file2", "w") as f:
            f.write("hallo")

        careful_copy_file("file1", "file2")
        with open("file2", "r") as f:
            assert "hallo" == f.readline()

        careful_copy_file("file1", "file3")
        assert  os.path.isfile("file3") 


if __name__ == "__main__":
    unittest.main()