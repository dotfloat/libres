#  Copyright (C) 2012  Equinor ASA, Norway.
#
#  The file 'test_config.py' is part of ERT - Ensemble based Reservoir Tool.
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
import os
import pytest

from res import ResPrototype
from res.config import UnrecognizedEnum, SchemaItem
from res.config import ContentTypeEnum, ContentItem, ContentNode
from res.config import ConfigContent, ConfigParser, ConfigSettings


# Adding extra functions to the ConfigContent object for the ability
# to test low level C functions which are not exposed in Python.
_safe_iget      = ResPrototype("char* config_content_safe_iget(config_content, char*, int, int)")
_iget           = ResPrototype("char* config_content_iget(config_content, char*, int, int)")
_iget_as_int    = ResPrototype("int config_content_iget_as_int(config_content, char*, int, int)")
_iget_as_bool   = ResPrototype("bool config_content_iget_as_bool(config_content, char*, int, int)")
_iget_as_double = ResPrototype("double config_content_iget_as_double(config_content, char*, int, int)")
_get_occurences = ResPrototype("int config_content_get_occurences(config_content, char*)")


@pytest.fixture(scope="module")
def file_list():
    return []


def test_enums(res_helper):
    source_file_path = "lib/include/ert/config/config_schema_item.hpp"
    res_helper.assert_enum_fully_defined(ContentTypeEnum, "config_item_types", source_file_path)
    res_helper.assert_enum_fully_defined(UnrecognizedEnum, "config_schema_unrecognized_enum", source_file_path)


def test_item_types(tmpdir):
    with tmpdir.as_cwd():
        with open("config", "w") as f:
            f.write("TYPE_ITEM 10 3.14 TruE  String  file\n")

        conf = ConfigParser()
        assert len(conf) == 0

        schema_item = conf.add("TYPE_ITEM", False)
        schema_item.iset_type(0, ContentTypeEnum.CONFIG_INT)
        schema_item.iset_type(1, ContentTypeEnum.CONFIG_FLOAT)
        schema_item.iset_type(2, ContentTypeEnum.CONFIG_BOOL)
        schema_item.iset_type(3, ContentTypeEnum.CONFIG_STRING)
        schema_item.iset_type(4, ContentTypeEnum.CONFIG_PATH)
        assert len(conf) == 1
        assert "TYPE_XX" not in conf
        assert "TYPE_ITEM" in conf

        content = conf.parse("config")
        type_item = content["TYPE_ITEM"][0]
        int_value = type_item[0]
        assert int_value == 10
        assert type_item.igetString(0) == "10"

        float_value = type_item[1]
        assert float_value == 3.14
        assert type_item.igetString(1) == "3.14"

        bool_value = type_item[2]
        assert bool_value is True
        assert type_item.igetString(2) == "TruE"

        string_value = type_item[3]
        assert string_value == "String"
        assert type_item.igetString(3) == "String"

        path_value = type_item[4]
        assert path_value == "file"
        assert type_item.igetString(4) == "file"

        # test __getitem__
        assert conf["TYPE_ITEM"] is True
        with pytest.raises(KeyError):
            _ = conf["TYPE_XX"]

        assert "ConfigParser" in repr(conf)
        assert "size=1" in repr(conf)


def test_parse():
    conf = ConfigParser()
    conf.add("FIELD", False)
    schema_item = conf.add("RSH_HOST", False)
    assert isinstance(schema_item, SchemaItem)
    test_path = self.createTestPath("local/config/simple_config")
    content = conf.parse(test_path, unrecognized=UnrecognizedEnum.CONFIG_UNRECOGNIZED_IGNORE)
    assert content.isValid()


    content_item = content["RSH_HOST"]
    assert isinstance(content_item, ContentItem)
    assert len(content_item) == 1
    with pytest.raises(TypeError):
        content_item["BJARNE"]

    with pytest.raises(IndexError):
        content_item[10]

    content_node = content_item[0]
    assert isinstance(content_node, ContentNode)
    assert len(content_node) == 2
    assert content_node[1] == "be-lx633214:2"
    assert content_node.content(sep=",") == "be-lx655082:2,be-lx633214:2"
    assert content_node.content() == "be-lx655082:2 be-lx633214:2"


    content_item = content["FIELD"]
    assert len(content_item) == 5
    with pytest.raises(IOError):
        conf.parse("DoesNotExits")


def test_parse_invalid(tmpdir):
    with tmpdir.as_cwd():
        conf = ConfigParser()
        conf.add("INT", value_type=ContentTypeEnum.CONFIG_INT)

        with open("config","w") as fileH:
            fileH.write("INT xx\n")

        with pytest.raises(ValueError):
            conf.parse("config")

        content = conf.parse("config", validate=False)
        assert not content.isValid()
        assert len(content.getErrors()) == 1


def test_parse_deprecated(tmpdir):
    with tmpdir.as_cwd():
        conf = ConfigParser()
        item = conf.add("INT", value_type=ContentTypeEnum.CONFIG_INT)
        msg = "ITEM INT IS DEPRECATED"
        item.setDeprecated(msg)

        with open("config","w") as fileH:
            fileH.write("INT 100\n")

        content = conf.parse("config" )
        assert content.isValid()

        warnings = content.getWarnings()
        assert len(warnings) == 1
        assert warnings[0] == msg


def test_parse_dotdot_relative(tmpdir):
    with tmpdir.as_cwd():
        conf = ConfigParser()
        schema_item = conf.add("EXECUTABLE", False)
        schema_item.iset_type(0, ContentTypeEnum.CONFIG_PATH)

        os.makedirs("cwd/jobs")
        os.makedirs("eclipse/bin")
        script_path = str(tmpdir / "eclipse/bin/script.sh")
        with open(script_path,"w") as f:
            f.write("This is a test script")

        with open("cwd/jobs/JOB","w") as fileH:
            fileH.write("EXECUTABLE ../../eclipse/bin/script.sh\n")

        os.makedirs("cwd/ert")
        os.chdir("cwd/ert")
        content = conf.parse("../jobs/JOB")
        item = content["EXECUTABLE"]
        node = item[0]
        assert script_path == node.getPath()

    @tmpdir()
    def test_parser_content(self):
        conf = ConfigParser()
        conf.add("KEY2", False)
        schema_item = conf.add("KEY", False)
        schema_item.iset_type(2, ContentTypeEnum.CONFIG_INT)
        schema_item.iset_type(3, ContentTypeEnum.CONFIG_BOOL)
        schema_item.iset_type(4, ContentTypeEnum.CONFIG_FLOAT)
        schema_item.iset_type(5, ContentTypeEnum.CONFIG_PATH)
        schema_item = conf.add("NOT_IN_CONTENT", False)

        with open("config","w") as fileH:
            fileH.write("KEY VALUE1 VALUE2 100  True  3.14  path/file.txt\n")

        cwd0 = os.getcwd()
        os.makedirs("tmp")
        os.chdir("tmp")
        content = conf.parse("../config")
        d = content.as_dict()
        assert content.isValid()
        assert "KEY" in content
        assert not "NOKEY" in content
        assert cwd0 == content.get_config_path( )


        keys = content.keys()
        assert len(keys) == 1
        assert "KEY" in keys
        d = content.as_dict()
        assert "KEY" in d
        item_list = d["KEY"]
        assert len(item_list) == 1
        l = item_list[0]
        assert l[0] == "VALUE1"
        assert l[1] == "VALUE2"
        assert l[2] == 100
        assert l[3] == True
        assert l[4] == 3.14
        assert l[5] == "../path/file.txt"

        assert not "NOT_IN_CONTENT" in content
        item = content["NOT_IN_CONTENT"]
        assert len(item) == 0

        with pytest.raises(KeyError):
            content["Nokey"]

        item = content["KEY"]
        assert len(item) == 1


        line = item[0]
        with pytest.raises(TypeError):
            line.getPath(4)

        with pytest.raises(TypeError):
            line.getPath()


        rel_path = line.getPath(index=5, absolute=False)
        assert rel_path == "../path/file.txt"
        get = line[5]
        assert get == "../path/file.txt"
        abs_path = line.getPath(index=5)
        assert abs_path == os.path.join(cwd0, "path/file.txt")

        rel_path = line.getPath(index=5, absolute=False, relative_start="../")
        assert rel_path == "path/file.txt"


        with pytest.raises(IndexError):
            item[10]

        node = item[0]
        assert len(node) == 6
        with pytest.raises(IndexError):
            node[6]

        assert node[0] == "VALUE1"
        assert node[1] == "VALUE2"
        assert node[2] == 100
        assert node[3] == True
        assert node[4] == 3.14

        assert content.getValue("KEY", 0, 1) == "VALUE2"
        assert _iget(content, "KEY", 0, 1) == "VALUE2"

        assert content.getValue("KEY", 0, 2) == 100
        assert _iget_as_int(content, "KEY", 0, 2) == 100

        assert content.getValue("KEY", 0, 3) == True
        assert _iget_as_bool(content, "KEY", 0, 3) == True

        assert content.getValue("KEY", 0, 4) == 3.14
        assert _iget_as_double(content, "KEY", 0, 4) == 3.14

        assert _safe_iget(content, "KEY2", 0, 0) is None

        assert _get_occurences(content, "KEY2") == 0
        assert _get_occurences(content, "KEY") == 1
        assert _get_occurences(content, "MISSING-KEY") == 0

    def test_schema(self):
        schema_item = SchemaItem("TestItem")
        assert isinstance(schema_item, SchemaItem)
        assert schema_item.iget_type(6) == ContentTypeEnum.CONFIG_STRING
        schema_item.iset_type(0, ContentTypeEnum.CONFIG_INT)
        assert schema_item.iget_type(0) == ContentTypeEnum.CONFIG_INT
        schema_item.set_argc_minmax(3, 6)

        del schema_item

    @tmpdir()
    def test_settings(self):
        cs = ConfigSettings("SETTINGS")

        with pytest.raises(TypeError):
            cs.addSetting("SETTING1", ContentTypeEnum.CONFIG_INT, 100.67)

        assert not "SETTING1" in cs
        cs.addSetting("SETTING2", ContentTypeEnum.CONFIG_INT, 100)
        assert "SETTING2" in cs

        with pytest.raises(KeyError):
            value = cs["NO_SUCH_KEY"]

        assert cs["SETTING2"] == 100

        with pytest.raises(KeyError):
            cs["NO_SUCH_KEY"] = 100


        parser = ConfigParser()
        cs = ConfigSettings("SETTINGS")
        cs.addSetting("A", ContentTypeEnum.CONFIG_INT, 1)
        cs.addSetting("B", ContentTypeEnum.CONFIG_INT, 1)
        cs.addSetting("C", ContentTypeEnum.CONFIG_INT, 1)
        cs.initParser(parser)

        with open("config","w") as fileH:
            fileH.write("SETTINGS A 100\n")
            fileH.write("SETTINGS B 200\n")
            fileH.write("SETTINGS C 300\n")

        content = parser.parse("config")

        cs.apply(content)

        assert cs["A"] == 100
        assert cs["B"] == 200
        assert cs["C"] == 300

        keys = cs.keys()
        assert "A" in keys
        assert "B" in keys
        assert "C" in keys
        assert len(keys) == 3

        cs = ConfigSettings("SETTINGS")
        cs.addDoubleSetting("A", 1.0)
        assert ContentTypeEnum.CONFIG_FLOAT == cs.getType("A")

        cs = ConfigSettings("SETTINGS")
        cs.addDoubleSetting("A", 1.0)
        cs.addIntSetting("B", 1)
        cs.addStringSetting("C", "1")
        cs.addBoolSetting("D",  True)
        cs.initParser(parser)

        with open("config","w") as fileH:
            fileH.write("SETTINGS A 100.1\n")
            fileH.write("SETTINGS B 200\n")
            fileH.write("SETTINGS C 300\n")
            fileH.write("SETTINGS D False\n")

        content = parser.parse("config")

        cs.apply(content)
        assert cs["A"] == 100.1
        assert cs["B"] == 200
        assert cs["C"] == "300"
        assert cs["D"] == False

        with pytest.raises(Exception):
            cs["A"] = "Hei"

    @tmpdir()
    def test_add_unknown_keyowrds(self):
        parser = ConfigParser( )
        with open("config","w") as fileH:
            fileH.write("SETTINGS A 100.1\n")
            fileH.write("SETTINGS B 200  STRING1 STRING2\n")
            fileH.write("SETTINGS C 300\n")
            fileH.write("SETTINGS D False\n")

        content = parser.parse("config", unrecognized=UnrecognizedEnum.CONFIG_UNRECOGNIZED_ADD)

        assert "SETTINGS" in content
        item = content["SETTINGS"]
        assert len(item) == 4

        nodeA = item[0]
        assert nodeA[0] == "A"
        assert nodeA[1] == "100.1"
        assert len(nodeA) == 2

        nodeB = item[1]
        assert nodeB[0] == "B"
        assert nodeB[1] == "200"
        assert nodeB[3] == "STRING2"
        assert len(nodeB) == 4

        assert len(content) == 4


def test_valid_string_runtime_file(tmpdir):
    with tmpdir.as_cwd():
        with open("some_file" , "w") as f:
            f.write("This i.")
        assert ContentTypeEnum.CONFIG_RUNTIME_FILE.valid_string("no_file")
        assert ContentTypeEnum.CONFIG_RUNTIME_FILE.valid_string("some_file", True)
        assert not ContentTypeEnum.CONFIG_RUNTIME_FILE.valid_string("no_file", True)


def test_valid_string():
    assert ContentTypeEnum.CONFIG_FLOAT.valid_string("1.25")
    assert ContentTypeEnum.CONFIG_RUNTIME_INT.valid_string("1.7")
    assert not ContentTypeEnum.CONFIG_RUNTIME_INT.valid_string("1.7", runtime=True)
    assert ContentTypeEnum.CONFIG_FLOAT.valid_string("1.125", runtime=True)
    assert ContentTypeEnum.CONFIG_FLOAT.convert_string("1.25") == 1.25
    assert ContentTypeEnum.CONFIG_INT.convert_string("100") == 100

    with pytest.raises(ValueError):
        ContentTypeEnum.CONFIG_INT.convert_string("100x")

    with pytest.raises(ValueError):
        ContentTypeEnum.CONFIG_FLOAT.convert_string("100X")

    with pytest.raises(ValueError):
        ContentTypeEnum.CONFIG_BOOL.convert_string("a_random_string")

    assert ContentTypeEnum.CONFIG_BOOL.convert_string("TRUE")
    assert ContentTypeEnum.CONFIG_BOOL.convert_string("True")
    assert not ContentTypeEnum.CONFIG_BOOL.convert_string("False")
    assert not ContentTypeEnum.CONFIG_BOOL.convert_string("F")