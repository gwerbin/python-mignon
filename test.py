import json
from json_rpc import RPCServer, RPCError, NODATA


def add(params):
    for k in ('x', 'y'):
        try:
            v = params[k]
        except KeyError:
            raise RPCError('Missing parameter', k)

        if not isinstance(v, (int, float)):
            raise RPCError('Parameters must be numbers', k)

    return params['x'] + params['y']


server = RPCServer()
server.register('add', add)

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
        'method': 'multiply',
        'params': {'x': 1.7, 'y': 10}
    },
    # Invalid data
    {
        'jsonrpc': '2.0',
        'method': 'add',
        'params': {'x': '1.7', 'y': '10'}
    },
]

print('*** Testing RPC client ***')

for req in requests:
    print('==========')
    print(json.dumps(req, indent=2))
    print(json.dumps(server.call(req), indent=2))