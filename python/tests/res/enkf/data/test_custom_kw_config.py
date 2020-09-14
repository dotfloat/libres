from res.enkf.config.custom_kw_config import CustomKWConfig
from tests import ResTest
from tests.utils import tmpdir
from ecl.util.util import StringList


class CustomKWConfigTest(ResTest):

    def createResultFile(self, filename, data):
        with open(filename, "w") as output_file:
            for key in data:
                output_file.write("%s %s\n" % (key, data[key]))

    @tmpdir()
    def test_custom_kw_config_creation(self):
        data = {"VALUE_1": 2345.234,
                "VALUE_2": 0.001234,
                "VALUE_3": "string_1",
                "VALUE_4": "string_2"}

        self.createResultFile("result_file", data)

        custom_kw_config = CustomKWConfig("CUSTOM_KW", "result_file", "output_file")

        assert custom_kw_config.getName() == "CUSTOM_KW"
        assert custom_kw_config.getResultFile() == "result_file"
        assert custom_kw_config.getOutputFile() == "output_file"

        assert len(custom_kw_config) == 0

        result = StringList()
        success = custom_kw_config.parseResultFile("result_file", result)
        assert success

        assert len(custom_kw_config) == 4

        for index, key in enumerate(data):
            assert key in custom_kw_config

            key_is_string = isinstance(data[key], str)
            assert custom_kw_config.keyIsDouble(key) != key_is_string
            assert index == custom_kw_config.indexOfKey(key)

            assert result[index] == str(data[key])

        assert len(custom_kw_config.getKeys()) == 4

        for key in custom_kw_config:
            assert key in data

    @tmpdir()
    def test_custom_kw_config_multiple_identical_keys(self):
            data = {"VALUE_1": 2345.234,
                    "VALUE_2": 0.001234,
                    "VALUE_3": "string_1",
                    "VALUE_4": "string_2 VALUE_4 repeat_of_value_4"}

            self.createResultFile("result_file", data)

            custom_kw_config = CustomKWConfig("CUSTOM_KW", "result_file")

            result = StringList()
            success = custom_kw_config.parseResultFile("result_file", result)
            assert success

            index_of_value_4 = custom_kw_config.indexOfKey("VALUE_4")
            assert result[index_of_value_4] == "repeat_of_value_4"

    @tmpdir()
    def test_custom_kw_config_define_and_read(self):
            data_1 = {"VALUE_1": 123453.3,
                      "VALUE_2": 0.234234}

            data_2 = {"VALUE_1": 965689,
                      "VALUE_3": 1.1222}

            self.createResultFile("result_file_1", data_1)
            self.createResultFile("result_file_2", data_2)

            custom_kw_config = CustomKWConfig("CUSTOM_KW", "result_file")

            result_1 = StringList()
            success = custom_kw_config.parseResultFile("result_file_1", result_1)
            assert success

            result_2 = StringList()
            success = custom_kw_config.parseResultFile("result_file_2", result_2)
            assert not success

            for key in custom_kw_config:
                assert key in data_1

            assert not "VALUE_3" in custom_kw_config

    @tmpdir()
    def test_custom_kw_config_parse_fail(self):
            data = {"KEY_1": "Value Key_2"}

            self.createResultFile("result_file", data)

            custom_kw_config = CustomKWConfig("CUSTOM_KW_FAIL", "result_file")
            assert custom_kw_config.getOutputFile() is None

            assert not custom_kw_config.parseResultFile("result_file", StringList())

    def test_custom_kw_config_construction_with_definition(self):
        definition = {
            "VALUE_1": float,
            "VALUE_2": str
        }
        custom_kw_config = CustomKWConfig("TEST", None, definition=definition)
        assert len(custom_kw_config.getKeys()) == 2

        assert custom_kw_config.keyIsDouble("VALUE_1")
        assert not custom_kw_config.keyIsDouble("VALUE_2")

        assert "VALUE_1" in custom_kw_config
        assert "VALUE_2" in custom_kw_config
        assert "VALUE_3" not in custom_kw_config