"""
This module defines a decorator to convert request parameters to arguments for the view function.
"""

import builtins
import functools
import inspect
import keyword
import logging
import re
from typing import Any

import inflection

from ..http_facts import FORM_CONTENT_TYPES
from ..lifecycle import EspecificoRequest  # NOQA
from ..utils import all_json

logger = logging.getLogger(__name__)


def inspect_function_arguments(function):  # pragma: no cover
    """
    Returns the list of variables names of a function and if it
    accepts keyword arguments.

    :type function: Callable
    :rtype: tuple[list[str], bool]
    """
    parameters = inspect.signature(function).parameters
    bound_arguments = [
        name for name, p in parameters.items() if p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
    ]
    has_kwargs = any(p.kind == p.VAR_KEYWORD for p in parameters.values())
    return list(bound_arguments), has_kwargs


def snake_and_shadow(name):
    """
    Converts the given name into Pythonic form. Firstly it converts CamelCase names to snake_case.
    Secondly it looks to see if the name matches a known built-in and if it does it appends
    an underscore to the name.
    :param name: The parameter name
    :type name: str
    :return:
    """
    snake = inflection.underscore(name)
    if snake in builtins.__dict__ or keyword.iskeyword(snake):
        return f"{snake}_"
    return snake


def sanitized(name: str) -> str:
    """Change the argument so that it becomes a valid Python identifier."""
    return name and re.sub("^[^a-zA-Z_]+", "",
                           re.sub("[^0-9a-zA-Z_]", "",
                                  re.sub(r"\[(?!])", "_", name)))


def pythonic(name: str) -> str:
    """Change the argument so that it becomes an idiomatic Python identifier."""
    name = name and snake_and_shadow(name)
    return sanitized(name)


def parameter_to_arg(operation, function, pythonic_params=False, pass_context_arg_name=None):
    """
    Pass query and body parameters as keyword arguments to handler function.

    See (https://github.com/zalando/especifico/issues/59)
    :param operation: The operation being called
    :type operation: especifico.operations.AbstractOperation
    :param pythonic_params: When True CamelCase parameters are converted to snake_case and\
    an underscore is appended to any shadowed built-ins
    :type pythonic_params: bool
    :param pass_context_arg_name: If not None URL and function has an argument matching this name,\
    the framework's
    request context will be passed as that argument.
    :type pass_context_arg_name: str|None
    """
    consumes = operation.consumes

    sanitize = pythonic if pythonic_params else sanitized
    arguments, has_kwargs = inspect_function_arguments(function)

    @functools.wraps(function)
    def wrapper(request):
        # type: (EspecificoRequest) -> Any
        logger.debug("Function Arguments: %s", arguments)
        kwargs = {}

        if all_json(consumes):
            request_body = request.json
        elif consumes[0] in FORM_CONTENT_TYPES:
            request_body = request.form
        else:
            request_body = request.body

        try:
            query = request.query.to_dict(flat=False)
        except AttributeError:
            query = dict(request.query.items())

        kwargs.update(
            operation.get_arguments(
                request.path_params,
                query,
                request_body,
                request.files,
                arguments,
                has_kwargs,
                sanitize,
            ),
        )

        # optionally convert parameter variable names to un-shadowed, snake_case form
        if pythonic_params:
            kwargs = {snake_and_shadow(k): v for k, v in kwargs.items()}

        # add context info (e.g. from security decorator)
        for key, value in request.context.items():
            if has_kwargs or key in arguments:
                kwargs[key] = value
            else:
                logger.debug("Context parameter '%s' not in function arguments", key)

        # attempt to provide the request context to the function
        if pass_context_arg_name and (has_kwargs or pass_context_arg_name in arguments):
            kwargs[pass_context_arg_name] = request.context

        return function(**kwargs)

    return wrapper
