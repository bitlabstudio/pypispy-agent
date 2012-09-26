"""Tests for the ``PyPiSpy`` server side script."""
import json
import mock
import unittest

from pypispy import PyPiSpyAgent
import test_settings


def create_agent():
    agent = PyPiSpyAgent(
        test_settings.SERVER_NAME,
        test_settings.VENVS,
        test_settings.VENVS_DIR,
        test_settings.EMAIL,
        test_settings.API_KEY,
        test_settings.API_URL,)
    return agent


class FakeResponse(mock.Mock):
    """
    This is a substitution class for the ``call_url`` method of PyPiSpyAgent

    """
    status_code = mock.Mock()
    read = mock.Mock()


class PyPiSpyAgentTestCase(unittest.TestCase):
    """Tests for the ``PyPiSpyAgent`` class."""
    def setUp(self):
        self.expected_package_list = 'argparse==1.2.1\n-e hg+http://bitbucket.org/mbrochh/pypispy-bitbucket-test@788deeeeb6324bd9e042686ef8f436ad61be4f72#egg=pypispy_bitbucket_test-dev\n-e git://github.com/bitmazk/pypispy-github-test.git@15cea4f850b12e9bfb74b361e83780d180102d5c#egg=pypispy_github_test-dev\npypispy-pypi-test==0.1\nwsgiref==0.1.2\n'  # NOQA

    def test_init(self):
        agent = create_agent()
        self.assertEqual(agent.server_name, test_settings.SERVER_NAME,
            msg="Init should set the server name to '%s' but got '%s'"\
                % (test_settings.SERVER_NAME, agent.server_name))
        self.assertEqual(agent.venvs, test_settings.VENVS,
            msg="Init should set the virtual environments to '%s' but got '%s'"\
                % (test_settings.VENVS, agent.venvs))
        self.assertEqual(agent.venvs_dir, test_settings.VENVS_DIR,
            msg="Init should set the virtual environment directory to '%s' but\
                got '%s'" % (test_settings.VENVS_DIR, agent.venvs_dir))
        self.assertEqual(agent.email, test_settings.EMAIL,
            msg="Init should set the email to '%s' but got '%s'"\
                % (test_settings.EMAIL, agent.email))
        self.assertEqual(agent.api_key, test_settings.API_KEY,
            msg="Init should set the api key to '%s' but got '%s'"\
                % (test_settings.API_KEY, agent.api_key))

    def test_call_pypispy_api(self):  # TODO
        # create the agent and mock out the API call
        old_call_url = PyPiSpyAgent.call_url
        PyPiSpyAgent.call_url = FakeResponse()
        agent = create_agent()
        agent.call_url.read.return_value = 'success'
        data = {}

        # if response is not 'success' it should raise an exception
        agent.call_url.read.return_value = json.dumps(
            {'TestMessage': 'Test message to test this message.'})
        self.assertRaises(Exception, agent.call_pypispy_api, (),
            (data, agent.venvs[0]))

        PyPiSpyAgent.call_url = old_call_url

    def test_get_package_list(self):
        agent = create_agent()
        package_list = agent.get_package_list(agent.venvs[0])
        self.assertEqual(package_list, self.expected_package_list)

    def test_inspect_venv(self):
        agent = PyPiSpyAgent(
            test_settings.SERVER_NAME,
            test_settings.VENVS,
            test_settings.VENVS_DIR,
            test_settings.EMAIL,
            test_settings.API_KEY)
        data = agent.inspect_venv(agent.venvs[0])

        server_name = data.get('server_name')
        email = data.get('email')
        api_key = data.get('api_key')
        package_info = data.get('package_info')

        self.assertEqual(test_settings.SERVER_NAME, server_name,
            msg="Expected server name to be '%s' but go '%s'"\
                % (test_settings.SERVER_NAME, server_name))
        self.assertEqual(test_settings.API_KEY, api_key,
            msg="Expected api key to be '%s' but go '%s'"\
                % (test_settings.API_KEY, api_key))
        self.assertEqual(test_settings.EMAIL, email,
            msg="Expected email to be '%s' but go '%s'"\
                % (test_settings.EMAIL, email))
        self.assertEqual(package_info, self.expected_package_list,
            msg="Got wrong package info")

    def test_run(self):
        old_call_pypispy_api = PyPiSpyAgent.call_pypispy_api
        PyPiSpyAgent.call_pypispy_api = mock.Mock()
        agent = PyPiSpyAgent(
            test_settings.SERVER_NAME,
            test_settings.VENVS,
            test_settings.VENVS_DIR,
            test_settings.EMAIL,
            test_settings.API_KEY)
        agent.run()
        # test if called for each virtual environment
        self.assertEqual(agent.call_pypispy_api.call_count,
            len(test_settings.VENVS),
            msg="Call count doesn't match number of environments. \
                Expected '%s' but got '%s'" % (
                len(test_settings.VENVS),
                agent.call_pypispy_api.call_count)
            )
        PyPiSpyAgent.call_pypispy_api = old_call_pypispy_api
