
# Test experiment and model rename core logic

from mlflow_export_import.bulk.bulk_utils import replace_name

def test_equal():
    renames = { "/User/foo": "/User/bar" }
    new_name = replace_name("/User/foo" , renames)
    assert new_name == "/User/bar"

def test_prefix():
    renames = { "/User/foo": "/User/bar" }
    new_name = replace_name("/User/foo/home" , renames)
    assert new_name == "/User/bar/home"

def test_no_match():
    renames = { "/User/foo": "/User/bar" }
    new_name = replace_name("foo" , renames)
    assert new_name == "foo"

def test_blank_key():
    renames = { "": "/User/bar" }
    new_name = replace_name("foo" , renames)
    assert new_name == "foo"

def test_blank_key_2():
    renames = { "/User/foo": "/User/bar" }
    new_name = replace_name("" , renames)
    assert new_name == ""
