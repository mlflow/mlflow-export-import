from tests.databricks.init_tests import test_context
from tests.databricks import _test_registered_model

def test_registered_model(test_context):
    _test_registered_model.test_registered_model(test_context, True)
