import collections
import logging
from json import loads, dumps
from typing import Optional

import faker
from django import http
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.encoding import force_str

fake = faker.Faker()

logger = logging.getLogger(__name__)


class HttpMethod:
    GET = "get"
    POST = "post"
    PUT = "put"
    HEAD = "head"
    PATCH = "patch"
    OPTIONS = "options"
    DELETE = "delete"
    # NOTE: Test client has no trace method
    # TRACE = "trace"


def _format_data(d):
    if isinstance(d, (dict, list)):
        result = dumps(d, indent=4)
    elif isinstance(d, bytes):
        result = d.decode("utf-8", errors="replace")
    else:
        result = d
    return result


def _convert_cgi_formatted_header(h):
    return h.replace("HTTP_", "").replace("_", "-").title()


def _process_headers(headers):
    output = ""
    if headers:
        values = [f"{_convert_cgi_formatted_header(k)}: {v}" for k, v in headers.items()]
        output = "\n".join(values)
        output = f"\n{output}\n"
    return output


class BaseTestCase(TestCase):
    __test__ = True
    password = "asdfASDF1234"
    username = "testing"

    def tearDown(self) -> None:
        super().tearDown()
        self.client.logout()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=cls.username, email="testing@ag.com")
        cls.user.set_password(cls.password)
        cls.user.save()

    def authenticate(self, username: Optional[str] = None, password: Optional[str] = None):
        if username is None:
            username = self.user.username

        password = password or self.password
        data = {
            "username": username,
            "password": password,
        }
        self.assertTrue(self.client.login(**data))

    def format_request_info(self, response) -> str:
        query_string = response.request.get("QUERY_STRING")
        if query_string:
            query_string = f"?{query_string}"
        request_path = f"{response.request['REQUEST_METHOD']} {response.request['PATH_INFO']}{query_string}"
        return request_path

    def assertResponseStatus(self, response, status_code=http.HttpResponse.status_code):
        try:
            content = response.content.decode("utf-8") or "[content empty]"
        except UnicodeDecodeError:
            # Probably not text. Leave it as bytes repr
            content = str(response.content)
        message = f"\n{self.format_request_info(response)}\nReceived status code => {response.status_code}, " \
                  f"expected status code => {status_code}, content => {content or '[content empty]'}"
        self.assertEqual(response.status_code, status_code, msg=message)

    def log_request_response(self, request_headers, request_data, response):
        content_data = None

        if "application/json" in response.get("content-type", ""):
            content_data = loads(response.content, object_pairs_hook=collections.OrderedDict) if response.content else content_data
        else:
            # We may be potentially returning something else entirely in this case just render it for debugging purposes
            content_data = response.content

        if logger.isEnabledFor(logging.DEBUG) and response.content is not None:
            logged_data = ""
            if not isinstance(request_data, dict):
                if isinstance(request_data, bytes):
                    request_data = request_data.decode("utf-8", errors="ignore")

                # Prevent extra newlines in logged output
                decoded = force_str(request_data, errors="ignore")
                if decoded:
                    logged_data = f"\n{decoded}"

            request_headers = _process_headers(request_headers)
            request_path = self.format_request_info(response)

            # We may occasionally need to log things that can't be encoded easily via ascii codec to unicode
            logger.debug("%s::request =>\n\n%s%s%s\n%s\nHTTP %s %s\n%s\n%s\n",
                         self.__class__.__name__,
                         request_path,
                         request_headers.rstrip(),
                         logged_data,
                         "-" * 120,
                         response.status_code,
                         response.reason_phrase,
                         response.serialize_headers().decode("utf-8"),
                         _format_data(content_data))
        return content_data

    def request(self,  # type: ignore
                method: HttpMethod,
                url: str,
                data=None,
                authenticated=True,
                content_type="application/json",
                **extra):

        # Go ahead and encode data into a JSON string unless it's data that should be applied to
        # query strings.  In that case we just leave it alone and let the Client handle it
        if data:
            if method not in (HttpMethod.GET, HttpMethod.OPTIONS, HttpMethod.HEAD):
                if content_type == "application/json":
                    # Use our JSON encoder
                    data = dumps(data, indent=4)
                elif method in (HttpMethod.PUT, HttpMethod.PATCH):
                    # Django's test client does not encode data for `patch` and `put` the same way it does `post`
                    # Here we're manually encoding it such that we may `patch` or `put` things such as
                    # file uploads within the test client.
                    data = self.client._encode_data(data, content_type)
        else:
            data = ""

        func = getattr(self.client, method)

        if authenticated:
            self.authenticate()

        url = url or self.url

        response = func(path=url, data=data, content_type=content_type, **extra)
        extra["HTTP_CONTENT_TYPE"] = content_type
        content = self.log_request_response(request_headers=extra, request_data=data, response=response)

        return response, content
