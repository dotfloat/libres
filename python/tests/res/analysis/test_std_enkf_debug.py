#  Copyright (C) 2016  Equinor ASA, Norway.
#
#  The file 'test_analysis_module.py' is part of ERT - Ensemble based Reservoir Tool.
#
#  ERT is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ERT is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.
#
#  See the GNU General Public License at <http://www.gnu.org/licenses/gpl.html>
#  for more details.
import sys
import os

import pytest

from tests import ResTest
from res.analysis import AnalysisModule, AnalysisModuleLoadStatusEnum, AnalysisModuleOptionsEnum
from ecl.util.enums import RngAlgTypeEnum, RngInitModeEnum
from ecl.util.util.rng import RandomNumberGenerator

def find_file(path, filter):
    import fnmatch
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, filter):
            return os.path.join(root, filename)
    return None

class StdEnKFDebugTest(ResTest):

    def setUp(self):
        self.rng = RandomNumberGenerator(RngAlgTypeEnum.MZRAN, RngInitModeEnum.INIT_DEFAULT)
        if sys.platform.lower() == 'darwin':
            lib_name = "std_enkf_debug.dylib"
        else:
            lib_name = "std_enkf_debug.so"
        self.libname = find_file(self.SOURCE_ROOT, lib_name)
        if self.libname:
            self.module = AnalysisModule(lib_name = self.libname)
        else:
            pytest.skip('Debug library not found')


    def toggleKey(self, key):
        assert  self.module.hasVar( key )

        # check it is true
        assert  self.module.setVar( key , True ) 
        assert  self.module.getBool(key) 

        # set it to false
        assert  self.module.setVar( key , False ) 
        assert not  self.module.getBool(key) 

    def test_EE_option(self):
        self.toggleKey( 'USE_EE' )


    def test_scaledata_option(self):
        self.toggleKey( 'ANALYSIS_SCALE_DATA' )

    def test_prefix(self):
        assert  self.module.hasVar("PREFIX")
        assert  self.module.setVar( "PREFIX" , "Path") 