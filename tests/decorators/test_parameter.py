from unittest.mock import MagicMock

from especifico.decorators.parameter import parameter_to_arg, pythonic


def test_injection():
    request = MagicMock(name="request", path_params={"p1": "123"})
    request.args = {}
    request.headers = {}
    request.params = {}

    func = MagicMock()

    def handler(**kwargs):
        func(**kwargs)

    class Op:
        consumes = ["application/json"]

        def get_arguments(self, *args, **kwargs):
            return {"p1": "123"}

    parameter_to_arg(Op(), handler)(request)
    func.assert_called_with(p1="123")

    parameter_to_arg(Op(), handler, pass_context_arg_name="framework_request_ctx")(request)
    func.assert_called_with(p1="123", framework_request_ctx=request.context)


def test_pythonic_params():
    assert pythonic("orderBy[eq]") == "order_by_eq"
    assert pythonic("ids[]") == "ids"
