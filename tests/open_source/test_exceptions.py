import json
from mlflow_export_import.common import MlflowExportImportException
#from mlflow_export_import.common.mlflow_utils import dump_exception
from mlflow.exceptions import MlflowException
from mlflow.exceptions import RestException
from mlflow.exceptions import BAD_REQUEST, INTERNAL_ERROR
from mlflow.exceptions import ErrorCode


_msg_base = "foo"
_msg_child = "bar"

# == Test just Exception

def test_plain_exception():
    ex = Exception(_msg_base)
    assert _msg_base == str(ex)


# == Test MlflowException

def test_MLflowException():
    ex = MlflowException(_msg_base, error_code=BAD_REQUEST)
    assert _msg_base == ex.message
    assert _msg_base == str(ex)
    assert _msg_base == _to_dct(ex.serialize_as_json()).get("message",None)
    assert ex.error_code == ErrorCode.Name(BAD_REQUEST)


def test_RestException():
    str_error_code = ErrorCode.Name(BAD_REQUEST)
    ex = RestException({"message": _msg_base, "error_code": str_error_code })
    expected_msg = f"{str_error_code}: {_msg_base}" # NOTE: Bizarre, completely different format then MlflowException
    assert expected_msg == ex.message
    assert expected_msg == str(ex)
    assert expected_msg == _to_dct(ex.serialize_as_json()).get("message",None)
    assert ex.error_code == str_error_code


# == Test MlflowExportImportException with MLflowException

# Test with string CTOR argument
def test_ctor_string():
    ex = MlflowExportImportException(_msg_base)
    _assert_messages(ex, _msg_base, None)
    assert ex.src_exception == None
    assert ex.http_status_code == MlflowExportImportException.DEFAULT_HTTP_STATUS_CODE


# Test with MlflowException CTOR argument 
def test_ctor_exception():
    ex1 = MlflowException(_msg_base)
    ex2 = MlflowExportImportException(ex1)
    _assert_ex(ex1, ex2, _msg_base, None)


# Test with MlflowException CTOR argument with message
def test_ctor_exception_message():
    ex1 = MlflowException(_msg_base, error_code=BAD_REQUEST)
    ex2 = MlflowExportImportException(ex1, _msg_child)
    _assert_ex(ex1, ex2, _msg_child, _msg_base, BAD_REQUEST)


# == Test MlflowExportImportException with Exception CTOR

# Test with plain Exception CTOR argument 
def test_ctor_exception_2():
    ex1 = Exception(_msg_base)
    ex2 = MlflowExportImportException(ex1)
    _assert_messages(ex2, _msg_base, None)


# Test with Exception CTOR argument with message
def test_ctor_exception_message_2():
    ex1 = Exception(_msg_base)
    ex2 = MlflowExportImportException(ex1, _msg_child)
    _assert_ex(ex1, ex2, _msg_child, _msg_base)


# Test kwargs
def test_kwargs():
    ex = MlflowExportImportException(_msg_base, reason="Ouch", year=2023)
    _assert_message(ex, "reason", "Ouch")
    _assert_message(ex, "year", 2023)

# == Helper

def _assert_ex(ex1, ex2, msg, src_msg, mlflow_error_code=INTERNAL_ERROR):
    #dump_exception(ex1,"assert_ex Ex1")
    #dump_exception(ex2,"assert_ex Ex2")
    _assert_messages(ex2, msg, src_msg)
    assert ex2.src_exception == ex1
    if issubclass(ex1.__class__, MlflowException):
        assert ex2.http_status_code == ex1.get_http_status_code()
        assert ex1.error_code == ex2.kwargs.get("mlflow_error_code", None)
        assert ex1.error_code == ErrorCode.Name(mlflow_error_code)


def _assert_messages(ex, msg, src_msg):
    _assert_message(ex, "message", msg)
    assert ex.message == msg
    _assert_message(ex, "src_message", src_msg)
    assert ex.src_message == src_msg


def _assert_message(ex, key, msg):
    assert ex.kwargs.get(key, None) == msg


def _to_dct(json_str):
    return json.loads(json_str)
