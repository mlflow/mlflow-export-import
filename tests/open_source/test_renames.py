
# Test experiment and model rename core logic

from mlflow_export_import.bulk import rename_utils

def test_equal():
    renames = { "/User/foo": "/User/bar" }
    new_name = rename_utils.rename("/User/foo" , renames)
    assert new_name == "/User/bar"

def test_prefix():
    renames = { "/User/foo": "/User/bar" }
    new_name = rename_utils.rename("/User/foo/home" , renames)
    assert new_name == "/User/bar/home"

def test_no_match():
    renames = { "/User/foo": "/User/bar" }
    new_name = rename_utils.rename("foo" , renames)
    assert new_name == "foo"

def test_blank_key():
    renames = { "": "/User/bar" }
    new_name = rename_utils.rename("foo" , renames)
    assert new_name == "foo"

def test_blank_key_2():
    renames = { "/User/foo": "/User/bar" }
    new_name = rename_utils.rename("" , renames)
    assert new_name == ""
