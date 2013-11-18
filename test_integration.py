import unittest
import json
from mock import patch
from collections import namedtuple
from integration import create_app, remove_app


class IntegrationTestCase(unittest.TestCase):

    @patch("requests.post")
    def test_create_app_should_post_and_repass_message(self, post):
        post.return_value = namedtuple("Response", ["text"])(text="app created")
        r = create_app()
        self.assertEqual("app created", r)

    @patch("requests.post")
    def test_create_app_should_call_correct_url(self, post):
        create_app()
        url = post.call_args[0][0]
        self.assertEqual("http://localhost:8888/apps", url)

    @patch("requests.post")
    def test_create_app_should_pass_correct_json(self, post):
        create_app()
        got = json.loads(post.call_args[0][1])
        expected = {"name": "integration", "platform": "static"}
        self.assertEqual(expected, got)

    @patch("requests.delete")
    def test_remove_app_should_delete_and_repass_message(self, delete):
        delete.return_value = namedtuple("Response", ["text"])(text="app removed")
        r = remove_app()
        self.assertEqual("app removed", r)

    @patch("requests.delete")
    def test_remove_app_should_call_right_url(self, delete):
        remove_app()
        url = delete.call_args[0][0]
        self.assertEqual("http://localhost:8888/apps/integration", url)


if __name__ == "__main__":
    unittest.main()
