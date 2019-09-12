import json
from json_rpc import RPCServer, RPCError, RPCErrorCode, NODATA


def add(x, y):
    return x + y


def rpc_add(params):
    for k in ('x', 'y'):
        try:
            v = params[k]
        except KeyError:
            raise RPCError(RPCErrorCode.INVALID_PARAMS, 'Missing parameter', k)

        if not isinstance(v, (int, float)):
            raise RPCError(RPCErrorCode.INVALID_PARAMS, 'Parameters must be numbers', k)

    return add(**params)


server = RPCServer()
server.register('add', rpc_add)

requests = [
    # OK request
    {
        'jsonrpc': '2.0',
        'id': '123',
        'method': 'add',
        'params': {'x': 1.7, 'y': 10}
    },
    # Invalid protocol
    {
        'jsonrpc': '1.0',
        'id': '123',
        'method': 'add',
        'params': {'x': 1.7, 'y': 10}
    },
    # Missing ID
    {
        'jsonrpc': '2.0',
        'method': 'add',
        'params': {'x': 1.7, 'y': 10}
    },
    # Unknown method
    {
        'jsonrpc': '2.0',
        'id': '123',
        'method': 'multiply',
        'params': {'x': 1.7, 'y': 10}
    },
    # Invalid data
    {
        'jsonrpc': '2.0',
        'id': '123',
        'method': 'add',
        'params': {'x': '1.7', 'y': '10'}
    },
    # Invalid params, un-handled
    {
        'jsonrpc': '2.0',
        'id': '123',
        'method': 'add',
        'params': {'x': 1.7, 'y': 10, 'z': 'hello'}
    },
]

print('*** Testing RPC client ***')

for req in requests:
    print('==========')
    print(json.dumps(req, indent=2))
    print(json.dumps(server.call(req, handle_unknown_errors=True), indent=2))