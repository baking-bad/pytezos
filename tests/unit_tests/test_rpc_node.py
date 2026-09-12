from unittest import TestCase
from unittest.mock import Mock
from unittest.mock import patch

from pytezos.rpc.node import RpcError
from pytezos.rpc.node import RpcForbiddenError
from pytezos.rpc.node import RpcNode
from pytezos.rpc.node import RpcNotFoundError

MEMPOOL_PATH = '/chains/main/mempool/pending_operations'


def response(status_code: int, reason: str, text: str = '', content_type: str = 'text/html', json=None) -> Mock:
    res = Mock(status_code=status_code, reason=reason, text=text, headers={'content-type': content_type})
    res.json.return_value = json
    return res


class TestRpcNodeStatusErrors(TestCase):
    def get(self, res: Mock):
        with patch('pytezos.rpc.node.requests.request', return_value=res):
            return RpcNode('http://localhost:8732').get(MEMPOOL_PATH)

    def test_401_raises_forbidden(self) -> None:
        with self.assertRaises(RpcForbiddenError) as ctx:
            self.get(response(401, 'Unauthorized', text='unauthorized'))
        self.assertIn(MEMPOOL_PATH, str(ctx.exception))
        self.assertIn('Unauthorized', str(ctx.exception))

    def test_403_raises_forbidden(self) -> None:
        with self.assertRaises(RpcForbiddenError) as ctx:
            self.get(response(403, 'Forbidden', text='<html>forbidden</html>'))
        self.assertIn('Forbidden', str(ctx.exception))

    def test_message_does_not_depend_on_reason_phrase(self) -> None:
        with self.assertRaises(RpcForbiddenError) as ctx:
            self.get(response(401, ''))
        self.assertEqual(f'Unauthorized: {MEMPOOL_PATH}', ctx.exception.args[0])

    def test_403_with_json_object_body_raises_forbidden(self) -> None:
        with self.assertRaises(RpcForbiddenError):
            self.get(response(403, 'Forbidden', content_type='application/json', json={'error': 'ACL: denied'}))

    def test_404_raises_not_found(self) -> None:
        with self.assertRaises(RpcNotFoundError) as ctx:
            self.get(response(404, 'Not Found', text='not found'))
        self.assertIn(MEMPOOL_PATH, str(ctx.exception))

    def test_status_errors_are_rpc_errors(self) -> None:
        self.assertTrue(issubclass(RpcForbiddenError, RpcError))
        self.assertTrue(issubclass(RpcNotFoundError, RpcError))
        with self.assertRaises(RpcError):
            self.get(response(401, 'Unauthorized'))
        with self.assertRaises(RpcError):
            self.get(response(404, 'Not Found'))

    def test_other_status_with_json_object_body_raises_rpc_error(self) -> None:
        body = {'error': 'rate limited'}
        with self.assertRaises(RpcError) as ctx:
            self.get(response(429, 'Too Many Requests', content_type='application/json', json=body))
        self.assertEqual(body, ctx.exception.args[0])

    def test_subclass_without_error_id_does_not_register_handler(self) -> None:
        self.assertNotIn(RpcForbiddenError, RpcError.__handlers__.values())
        self.assertNotIn(RpcNotFoundError, RpcError.__handlers__.values())
