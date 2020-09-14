import pytest
from res.util.substitution_list import SubstitutionList


def test_substitution_list():
    subst_list = SubstitutionList()
    subst_list.addItem("Key", "Value", "Doc String")

    assert len(subst_list) == 1

    with pytest.raises(KeyError):
        item = subst_list[2]

    with pytest.raises(KeyError):
        item = subst_list["NoSuchKey"]

    with pytest.raises(KeyError):
        item = subst_list.doc("NoSuchKey")

    assert "Key" in subst_list
    assert subst_list["Key"] == "Value"
    assert subst_list.doc("Key") == "Doc String"

    subst_list.addItem("Key2", "Value2", "Doc String2")
    assert len(subst_list) == 2

    keys = subst_list.keys( )
    assert keys[0] == "Key"
    assert keys[1] == "Key2"

    assert "Key" in str(subst_list)
    assert "SubstitutionList" in repr(subst_list)
    assert "2" in repr(subst_list)

    assert subst_list.get("nosuchkey", 1729) == 1729
    assert subst_list.get("nosuchkey") is None
    assert subst_list.get(513) is None
    for key in ('Key', 'Key2'):
        assert subst_list[key] == subst_list.get(key)