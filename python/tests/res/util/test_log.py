from res.util.enums import MessageLevelEnum


def test_enums(res_helper):
    res_helper.assert_enum_fully_defined(MessageLevelEnum, "message_level_type", "lib/include/ert/res_util/log.hpp")