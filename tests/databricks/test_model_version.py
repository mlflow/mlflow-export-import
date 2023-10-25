from tests.databricks.init_tests import test_context
from tests.databricks import _test_model_version

def test_import_metadata_false(test_context):
    _test_model_version.test_import_metadata_false(test_context, False)

def test_import_metadata_true(test_context):
    _test_model_version.test_import_metadata_true(test_context, False)
