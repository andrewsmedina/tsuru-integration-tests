import unittest
import json
from mock import patch, ANY, call
from os import path
from collections import namedtuple
from integration import (create_app, remove_app, deploy, create_user,
                         login, remove_user, auth_request, APP_NAME,
                         _clone_repository, _push_repository, TEST_REPOSITORY,
                         add_key, remove_key, add_team, remove_team)


class AppIntegrationTestCase(unittest.TestCase):

    @patch("requests.post")
    def test_create_app_should_post_and_return_app_repository(self, post):
        data = {"status":"success", "repository_url":"git@tsuru.io:repo.git"}
        post.return_value = namedtuple("Response", ["status_code", "json"])(status_code=200, json=lambda:data)
        r = create_app("token123")
        self.assertEqual("git@tsuru.io:repo.git", r)

    @patch("requests.post")
    def test_create_app_should_post_with_error_and_return_empty_repository_url(self, post):
        data = {"status":"some error", "repository_url":"git@tsuru.io:repo.git"}
        post.return_value = namedtuple("Response", ["status_code", "json"])(status_code=500, json=lambda:data)
        r = create_app("token123")
        self.assertEqual("", r)

    @patch("requests.post")
    def test_create_app_should_call_correct_url(self, post):
        create_app("token123")
        post.assert_called_once_with("http://localhost:8888/apps", headers=ANY, data=ANY)

    @patch("requests.post")
    def test_create_app_should_pass_correct_json(self, post):
        create_app("token123")
        expected = json.dumps({"name": APP_NAME, "platform": "static"})
        post.assert_called_once_with(ANY, headers=ANY, data=expected)

    @patch("integration.auth_request")
    def test_create_app_should_call_auth_request(self, auth_request):
        create_app("token123")
        auth_request.assert_called_once_with(ANY, ANY, ANY, data=ANY)

    @patch("integration.auth_request")
    def test_create_app_should_pass_token_to_auth_request(self, auth_request):
        create_app("token321")
        auth_request.assert_called_once_with(ANY, ANY, "token321", data=ANY)

    @patch("requests.delete")
    def test_remove_app_should_delete_and_repass_message(self, delete):
        delete.return_value = namedtuple("Response", ["text"])(text="app removed")
        r = remove_app("token123")
        self.assertEqual("app removed", r)

    @patch("requests.delete")
    def test_remove_app_should_call_right_url(self, delete):
        remove_app("token123")
        delete.assert_called_once_with("http://localhost:8888/apps/integration", headers=ANY)

    @patch("integration.auth_request")
    def test_remove_app_should_pass_token_to_auth_request(self, auth_request):
        remove_app("token321")
        auth_request.assert_called_once_with(ANY, ANY, "token321")


class UserIntegrationTestCase(unittest.TestCase):

    @patch("requests.post")
    def test_create_user_should_post_to_right_url(self, post):
        create_user()
        url = "http://localhost:8888/users"
        post.assert_called_once_with(url, ANY)

    @patch("requests.post")
    def test_create_user_should_pass_correct_json(self, post):
        create_user()
        expected = json.dumps({"email": "tester@globo.com", "password": "123456"})
        post.assert_called_once_with(ANY, expected)

    @patch("requests.delete")
    def test_remove_user_should_delete_to_right_url(self, delete):
        remove_user("token123")
        url = "http://localhost:8888/users"
        delete.assert_called_once_with(url, headers=ANY)

    @patch("integration.auth_request")
    def test_remove_user_should_pass_token_to_auth_request(self, auth_request):
        remove_user("token321")
        auth_request.assert_called_once_with(ANY, ANY, "token321")

    @patch("requests.post")
    def test_login_should_post_to_right_url(self, post):
        login()
        url = "http://localhost:8888/users/tester@globo.com/tokens"
        post.assert_called_once_with(url, ANY)

    @patch("requests.post")
    def test_login_should_post_correct_json(self, post):
        login()
        expected = json.dumps({"password": "123456"})
        post.assert_called_with(ANY, expected)

    @patch("requests.post")
    def test_login_should_return_token(self, post):
        post.return_value = namedtuple("Response", ["text", "status_code"])(text='{"token":"abc123"}', status_code=200)
        self.assertEqual("abc123", login())

    @patch("requests.post")
    def test_add_key_should_call_right_url(self, post):
        add_key("token123")
        post.assert_called_once_with("http://localhost:8888/users/keys", headers=ANY, data=ANY)

    @patch("requests.post")
    def test_add_key_should_pass_public_key_from_ssh_dir(self, post):
        f = open(path.expanduser("~/.ssh/id_rsa.pub"))
        key = f.read()
        f.close()
        data = json.dumps({"key": key})
        add_key("token123")
        post.assert_called_once_with(ANY, headers=ANY, data=data)

    @patch("integration.auth_request")
    def test_add_key_should_call_auth_request(self, auth_request):
        add_key("token321")
        auth_request.assert_called_once_with(ANY, ANY, "token321", data=ANY)

    @patch("requests.delete")
    def test_remove_key_should_call_right_url(self, delete):
        url = "http://localhost:8888/users/keys"
        remove_key("token123")
        delete.assert_called_once_with(url, headers=ANY, data=ANY)

    @patch("requests.delete")
    def test_remove_key_should_pass_public_key_from_ssh_dir(self, delete):
        f = open(path.expanduser("~/.ssh/id_rsa.pub"))
        key = f.read()
        f.close()
        data = json.dumps({"key": key})
        remove_key("token123")
        delete.assert_called_once_with(ANY, headers=ANY, data=data)

    @patch("integration.auth_request")
    def test_remove_key_should_call_auth_request(self, auth_request):
        remove_key("token321")
        auth_request.assert_called_once_with(ANY, ANY, "token321", data=ANY)

    @patch("requests.post")
    def test_add_team_should_post_to_right_url(self, post):
        url = "http://localhost:8888/teams"
        add_team("token123")
        post.assert_called_once_with(url, headers=ANY, data=ANY)

    @patch("requests.post")
    def test_add_team_should_post_team_name_in_body(self, post):
        add_team("token123")
        post.assert_called_once_with(ANY, headers=ANY, data=json.dumps({"name": "testteam"}))

    @patch("integration.auth_request")
    def test_add_team_should_call_auth_request(self, auth_request):
        add_team("token321")
        auth_request.assert_called_once_with(ANY, ANY, "token321", data=ANY)

    @patch("requests.delete")
    def test_remove_team_should_delete_to_right_url(self, delete):
        url = "http://localhost:8888/teams/testteam"
        remove_team("token123")
        delete.assert_called_once_with(url, headers=ANY)

    @patch("integration.auth_request")
    def test_remove_team_should_call_auth_request(self, auth_request):
        remove_team("token321")
        auth_request.assert_called_once_with(ANY, ANY, "token321")

class FakePost(object):
    def __call__(self, url, headers, **kwargs):
        self.url = url
        self.headers = headers
        self.kwargs = kwargs


class AuthenticatedRequestTestCase(unittest.TestCase):

    def test_should_add_Authentication_header_to_request(self):
        post = FakePost()
        auth_request(post, "test.com", "token321")
        auth = post.headers["Authorization"]
        self.assertEquals(auth, "token321")

    def test_should_pass_url_to_request(self):
        post = FakePost()
        auth_request(post, "test.com", "token123")
        self.assertEquals("test.com", post.url)

    def test_should_pass_kwargs_to_request(self):
        post = FakePost()
        auth_request(post, "test.com", "token123", test="foo", bar="test")
        self.assertDictEqual({"test":"foo", "bar":"test"}, post.kwargs)


class DeployTestCase(unittest.TestCase):

    @patch("subprocess.call")
    def test_clone_repository_should_call_git_clone(self, call):
        repo = "git@github.com/user/repo.git"
        dst = "/tmp"
        _clone_repository(repo, dst)
        call.assert_called_once_with(["git", "clone", repo, dst])

    @patch("subprocess.call")
    def test_push_repository_should_call_git_push(self, call):
        remote = "git@git.tsuru.io:user/repo.git"
        _push_repository(remote, "/tmp/repo/.git")
        call.assert_called_once_with(["git", "--git-dir=/tmp/repo/.git", "push", remote, "master"])

    @patch("subprocess.call")
    def test_deploy_should_call_git_push_with_remote_from_parameter_and_git_dir(self, call):
        remote = "git@localhost:integration.git"
        deploy(remote)
        call.assert_called_with(["git", "--git-dir=/tmp/test_app/.git", "push", remote, "master"])

    @patch("subprocess.call")
    def test_deploy_should_call_clone_repository(self, subp_call):
        deploy("git@localhost:integration.git")
        expected = call(["git", "clone", TEST_REPOSITORY, "/tmp/test_app"])
        self.assertEqual(expected, subp_call.call_args_list[0])


if __name__ == "__main__":
    unittest.main()
