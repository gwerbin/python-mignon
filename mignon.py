from enum import Enum
from typing import Mapping


class NODATA:
    pass


class RPCError(Exception):
    def __init__(self, code, message, data=NODATA):
        super().__init__(code, message)
        self.code = code
        self.message = message
        self.data = data

    def serialize(self):
        code = self.code
        obj = {
            'code': code.value if isinstance(code, RPCErrorCode) else code,
            'message': self.message
        }
        if self.data is not NODATA:
            obj['data'] = self.data
        return obj


class RPCErrorCode(Enum):
    # Standard error codes
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    # Implementation-defined error codes; reserved range is -32768 to -32000
    VALIDATOR_ERROR_UNHANLDED = -32101
    METHOD_ERROR_UNHANLDED = -32102


class RPCServer:
    """ RPC v2.0 protocol server """
    protocol_version = '2.0'

    _request_attributes_required = {'jsonrpc', 'method', 'id'}
    _request_attributes_optional = {'params'}

    def __init__(self):
        self._procedures = {}

    def register(self, method_name, method):
        self._procedures[method_name] = method

    def check_request(self, request):
        request_attributes = set(request)

        version = request.get('jsonrpc', None)
        if version != self.protocol_version:
            version_repr = repr(version) if version else "null"
            return RPCError(
                RPCErrorCode.INVALID_REQUEST,
                f'Incorrect protocol version; expected {self.protocol_version!r}, received {version_repr}.',
                data={'required_protocol_version': self.protocol_version}
            )

        missing_attributes = self._request_attributes_required - request_attributes
        if missing_attributes:
            return RPCError(
                RPCErrorCode.INVALID_REQUEST,
                f'Missing attributes: {",".join(map(repr, missing_attributes))}.',
                data=list(missing_attributes)
            )

        extra_attributes = request_attributes - (self._request_attributes_required | self._request_attributes_optional)
        if extra_attributes:
            return RPCError(
                RPCErrorCode.INVALID_REQUEST,
                f'Unrecognized attributes: {",".join(map(repr, extra_attributes))}.',
                data=list(missing_attributes)
            )

        if request['id'] is not None and not isinstance(request['id'], (str, int, float)):
            return RPCError(
                RPCErrorCode.INVALID_REQUEST,
                f'Request ID must be a string, a real number, or null.'
            )

    def _call(self, request, handle_unknown_errors=False):
        response = {
            'jsonrpc': self.protocol_version,
            'id': None
        }

        err = self.check_request(request)
        if err:
            response['error'] = err.serialize()
            return response

        response['id'] = request['id']
        method_name = request['method']
        params = request['params']

        try:
            method = self._procedures[method_name]
        except KeyError:
            error = RPCError(
                RPCErrorCode.METHOD_NOT_FOUND,
                f'Method {method_name} not found.'
            )
            response['error'] = error.serialize()
            return response

        try:
            result = method(params)
        except RPCError as exc:
            response['error'] = exc.serialize()
        except Exception as exc:
            if not handle_unknown_errors:
                raise exc
            error = RPCError(
                RPCErrorCode.METHOD_ERROR_UNHANLDED,
                'Unknown error while executing procedure',
                data=str(exc)
            )
            response['error'] = error.serialize()
        else:
            response['result'] = result

        return response

    def call(self, request, handle_unknown_errors=False):
        if isinstance(request, Mapping):
            # single request
            return self._call(request, handle_unknown_errors=handle_unknown_errors)
        else:
            # batch request
            return [self._call(req, handle_unknown_errors=handle_unknown_errors) for req in request]


if __name__ == '__main__':
    test()
