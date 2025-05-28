from unittest import IsolatedAsyncioTestCase
from sbilifeco.cp.common.http.client import HttpClient
from requests import Request


class HttpClientTest(IsolatedAsyncioTestCase):
    async def test_http_client(self):
        client = HttpClient().set_proto("http").set_host("tech101.in").set_port(80)

        req = Request(
            method="GET",
            url=client.url_base,
        )

        response = await client.request_as_binary(req)
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None
        html = response.payload.decode("utf-8")
        self.assertIn("WordPress", html, "Response is not genuine")
