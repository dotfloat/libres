import unittest
import os.path

from tests import ResTest, tmpdir
from res.test import ErtTestContext

from res.enkf import RunpathList, RunpathNode, ErtRunContext
from res.enkf.enums import EnkfInitModeEnum,EnkfRunType
from ecl.util.util import BoolVector
from res.util.substitution_list import SubstitutionList




def path(idx):
    return 'path_%d' % idx

def base(idx):
    return 'base_%d' % idx

class RunpathListTest(ResTest):

    @tmpdir()
    def test_load(self):
        with pytest.raises(IOError):
           rp = RunpathList("")

        node0 = RunpathNode(0,0,"path0","base0")
        node1 = RunpathNode(1,1,"path1","base1")

        runpath_list = RunpathList("filex.list")
        with pytest.raises(IOError):
            runpath_list.load( )

        with open("invalid_file","w") as f:
            f.write("X X X X\n")

        rp = RunpathList("invalid_file")
        with pytest.raises(IOError):
            rp.load()

        rp = RunpathList("list.txt")
        rp.add(node0.realization, node0.iteration, node0.runpath, node0.basename)
        rp.add(node1.realization, node1.iteration, node1.runpath, node1.basename)
        rp.export()
        assert os.path.isfile("list.txt")

        rp2 = RunpathList("list.txt")
        rp2.load()
        assert len(rp2) == 2
        assert rp2[0] == node0
        assert rp2[1] == node1

    def test_runpath_list(self):
        runpath_list = RunpathList('file')

        assert len(runpath_list) == 0

        test_runpath_nodes = [RunpathNode(0, 0, "runpath0", "basename0"), RunpathNode(1, 0, "runpath1", "basename0")]

        runpath_node = test_runpath_nodes[0]
        runpath_list.add(runpath_node.realization, runpath_node.iteration, runpath_node.runpath, runpath_node.basename)

        assert len(runpath_list) == 1
        assert runpath_list[0] == test_runpath_nodes[0]

        runpath_node = test_runpath_nodes[1]
        runpath_list.add(runpath_node.realization, runpath_node.iteration, runpath_node.runpath, runpath_node.basename)

        assert len(runpath_list) == 2
        assert runpath_list[1] == test_runpath_nodes[1]

        for index, runpath_node in enumerate(runpath_list):
            assert runpath_node == test_runpath_nodes[index]


        runpath_list.clear()

        assert len(runpath_list) == 0


    @tmpdir()
    def test_collection(self):
        """Testing len, adding, getting (idx and slice), printing, clearing."""
        runpath_list = RunpathList("EXPORT.txt")
        runpath_list.add( 3 , 1 , path(3) , base(3) )
        runpath_list.add( 1 , 1 , path(1) , base(1) )
        runpath_list.add( 2 , 1 , path(2) , base(2) )
        runpath_list.add( 0 , 0 , path(0) , base(0) )
        runpath_list.add( 3 , 0 , path(3) , base(3) )
        runpath_list.add( 1 , 0 , path(1) , base(1) )
        runpath_list.add( 2 , 0 , path(2) , base(2) )
        runpath_list.add( 0 , 1 , path(0) , base(0) )

        assert 8 == len(runpath_list)
        pfx = 'RunpathList(size' # the __repr__ function
        assert pfx == repr(runpath_list)[:len(pfx)]
        node2 = RunpathNode(2, 1 , path(2), base(2))
        assert node2 == runpath_list[2]

        node3 = RunpathNode(0,0,path(0),base(0))
        node4 = RunpathNode(3,0,path(3),base(3))
        node5 = RunpathNode(1,0,path(1),base(1))
        node6 = RunpathNode(2,0,path(2),base(2))
        nodeslice = [node3, node4, node5, node6]
        assert nodeslice == runpath_list[3:7]
        assert node6 == runpath_list[-2]
        with pytest.raises(TypeError):
            runpath_list["key"]
        with pytest.raises(IndexError):
            runpath_list[12]

        runpath_list.clear()
        assert 0 == len(runpath_list)
        with pytest.raises(IndexError):
            runpath_list[0]
        assert 'EXPORT.txt' == runpath_list.getExportFile()

    @tmpdir()
    def test_sorted_export(self):
        runpath_list = RunpathList("EXPORT.txt")
        runpath_list.add( 3 , 1 , "path" , "base" )
        runpath_list.add( 1 , 1 , "path" , "base" )
        runpath_list.add( 2 , 1 , "path" , "base" )
        runpath_list.add( 0 , 0 , "path" , "base" )

        runpath_list.add( 3 , 0 , "path" , "base" )
        runpath_list.add( 1 , 0 , "path" , "base" )
        runpath_list.add( 2 , 0 , "path" , "base" )
        runpath_list.add( 0 , 1 , "path" , "base" )

        runpath_list.export( )

        path_list = []
        with open("EXPORT.txt") as f:
          for line in f.readlines():
                tmp = line.split()
                iens = int(tmp[0])
                iteration = int(tmp[3])

                path_list.append( (iens , iteration) )

        for iens in range(4):
            t0 = path_list[iens]
            t4 = path_list[iens + 4]
            assert t0[0] == iens
            assert t4[0] == iens

            assert t0[1] == 0
            assert t4[1] == 1