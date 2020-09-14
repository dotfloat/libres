#!/usr/bin/env python
#  Copyright (C) 2013  Equinor ASA, Norway.
#
#  This file is part of ERT - Ensemble based Reservoir Tool.
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

import pytest

import os.path

from res.enkf import EclConfig, ResConfig, ConfigKeys
from tests import ResTest, tmpdir
from res.util import UIReturn
from ecl.summary  import EclSum

EGRID_file    = "Equinor/ECLIPSE/Gurbat/ECLIPSE.EGRID"
SMSPEC_file   = "Equinor/ECLIPSE/Gurbat/ECLIPSE.SMSPEC"
DATA_file     = "Equinor/ECLIPSE/Gurbat/ECLIPSE.DATA"
INIT_file     = "Equinor/ECLIPSE/Gurbat/EQUIL.INC"
DATA_INIT_file= "Equinor/ECLIPSE/Gurbat/ECLIPSE_INIT.DATA"





class EclConfigTest(ResTest):

    @pytest.mark.equinor_test
    def test_grid(self):
        grid_file = self.createTestPath( EGRID_file )
        smspec_file = self.createTestPath( SMSPEC_file )
        ec = EclConfig()
        ui = ec.validateGridFile( grid_file )
        assert  ui 
        assert  isinstance(ui , UIReturn )

        ui = ec.validateGridFile( "Does/Not/Exist" )
        assert not  ui 

        assert  os.path.exists( smspec_file )
        ui = ec.validateGridFile( smspec_file )
        assert not  ui 

    @pytest.mark.equinor_test
    def test_datafile(self):
        ec = EclConfig()
        ui = ec.validateDataFile( "DoesNotExist" )
        assert not  ui 

        dfile = self.createTestPath( DATA_file )
        ui = ec.validateDataFile( dfile )
        assert  ui 
        ec.setDataFile( dfile )
        assert dfile == ec.getDataFile()


    @pytest.mark.equinor_test
    def test_init_section(self):
        ec = EclConfig()
        dfile = self.createTestPath( DATA_file )
        difile = self.createTestPath( DATA_INIT_file )
        ifile = self.createTestPath( INIT_file )

        ui = ec.validateInitSection( ifile )
        assert not  ui 

        ec.setDataFile( dfile )
        ui = ec.validateInitSection( ifile )
        assert not  ui 

        ec.setDataFile( difile )
        ui = ec.validateInitSection( ifile )
        assert  ui 
        ec.setInitSection( ifile )
        assert  ifile , ec.getInitSection() 

    @pytest.mark.equinor_test
    def test_refcase( self ):
        ec = EclConfig()
        dfile = self.createTestPath( DATA_file )

        ui = ec.validateRefcase( "Does/not/exist" )
        assert not  ui 

        ui = ec.validateRefcase( dfile )
        assert  ui 
        ec.loadRefcase( dfile )
        refcase = ec.getRefcase()
        assert  isinstance( refcase , EclSum )
        refcaseName = ec.getRefcaseName() + ".DATA"
        assert dfile == refcaseName

    @tmpdir(local="configuration_tests")
    def test_ecl_config_constructor(self):
        config_dict = {
            ConfigKeys.DATA_FILE                : "configuration_tests/input/SPE1.DATA",
            ConfigKeys.ECLBASE                  : "configuration_tests/input/<ECLIPSE_NAME>-%d",
            ConfigKeys.GRID                     : "configuration_tests/input/CASE.EGRID",
            ConfigKeys.REFCASE                  : "configuration_tests/input/SNAKE_OIL_FIELD",
            ConfigKeys.END_DATE                 : "10/10/2010",
            ConfigKeys.SCHEDULE_PREDICTION_FILE : "configuration_tests/input/schedule.sch"
        }
        res_config = ResConfig('configuration_tests/ecl_config.ert')
        ecl_config_file = res_config.ecl_config
        ecl_config_dict = EclConfig(config_dict=config_dict)

        assert ecl_config_dict == ecl_config_file