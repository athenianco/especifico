"""
This module contains a mock resolver that returns mock functions for operations it cannot resolve.
"""

import functools
import logging

from especifico.resolver import Resolution, Resolver, ResolverError

logger = logging.getLogger(__name__)


class MockResolver(Resolver):
    """Mock resolver."""

    def __init__(self, mock_all):
        """Initialize a new instance of MockResolver."""
        super().__init__()
        self.mock_all = mock_all
        self._operation_id_counter = 1

    def resolve(self, operation):
        """
        Mock operation resolver

        :type operation: especifico.operations.AbstractOperation
        """
        operation_id = self.resolve_operation_id(operation)
        if not operation_id:
            # just generate an unique operation ID
            operation_id = f"mock-{self._operation_id_counter}"
            self._operation_id_counter += 1

        mock_func = functools.partial(self.mock_operation, operation=operation)
        if self.mock_all:
            func = mock_func
        else:
            try:
                func = self.resolve_function_from_operation_id(operation_id)
                logger.debug(
                    "... Successfully resolved operationId '%s'! Mock is *not* used for "
                    "this operation.", operation_id,
                )
            except ResolverError as resolution_error:
                logger.debug(
                    "... %s! Mock function is used for this operation.",
                    resolution_error.reason.capitalize(),
                )
                func = mock_func
        return Resolution(func, operation_id)

    def mock_operation(self, operation, *args, **kwargs):
        resp, code = operation.example_response()
        if resp is not None:
            return resp, code
        return "No example response was defined.", code
