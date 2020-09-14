# Copyright (C) 2017  Equinor ASA, Norway.
#
# This file is part of ERT - Ensemble based Reservoir Tool.
#
# ERT is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ERT is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.
#
# See the GNU General Public License at <http://www.gnu.org/licenses/gpl.html>
# for more details.
from os.path import abspath
from tests import ResTest, tmpdir

from ecl.grid import EclGridGenerator
from res.enkf.config import FieldTypeEnum, FieldConfig
from res.enkf.enums import EnkfFieldFileFormatEnum

class FieldConfigTest(ResTest):

    @tmpdir()
    def test_field_guess_filetype(self):
        fname = abspath('test.kw.grdecl')
        print(fname)
        with open(fname, 'w') as f:
            f.write("-- my comment\n")
            f.write("-- more comments\n")
            f.write("SOWCR\n")
            for i in range(256//8): # technicalities demand file has >= 256B
                f.write("0 0 0 0\n")

        ft = FieldConfig.guessFiletype(fname)
        grdecl_type = EnkfFieldFileFormatEnum(5)
        assert 'ECL_GRDECL_FILE' == grdecl_type.name
        assert grdecl_type == ft

    def test_field_type_enum(self):
        assert FieldTypeEnum(2) == FieldTypeEnum.ECLIPSE_PARAMETER
        gen = FieldTypeEnum.GENERAL
        assert 'GENERAL' == str(gen)
        gen = FieldTypeEnum(3)
        assert 'GENERAL' == str(gen)

    def test_export_format(self):
        assert FieldConfig.exportFormat("file.grdecl") == EnkfFieldFileFormatEnum.ECL_GRDECL_FILE
        assert FieldConfig.exportFormat("file.xyz.grdecl") == EnkfFieldFileFormatEnum.ECL_GRDECL_FILE
        assert FieldConfig.exportFormat("file.roFF") == EnkfFieldFileFormatEnum.RMS_ROFF_FILE
        assert FieldConfig.exportFormat("file.xyz.roFF") == EnkfFieldFileFormatEnum.RMS_ROFF_FILE

        with pytest.raises(ValueError):
            FieldConfig.exportFormat("file.xyz")

        with pytest.raises(ValueError):
            FieldConfig.exportFormat("file.xyz")

    def test_basics(self):
        grid = EclGridGenerator.create_rectangular((17,13,11),(1,1,1))
        fc = FieldConfig('PORO',grid)
        print(fc)
        print(str(fc))
        print(repr(fc))
        pfx = 'FieldConfig(type'
        rep = repr(fc)
        assert pfx == rep[:len(pfx)]
        fc_xyz = fc.get_nx(),fc.get_ny(),fc.get_nz()
        ex_xyz = 17,13,11
        assert ex_xyz == fc_xyz
        assert 0 == fc.get_truncation_mode()
        assert ex_xyz == (grid.getNX(), grid.getNY(), grid.getNZ())