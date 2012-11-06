"""
Runs `pip freeze` for your venvs. Sends data to the https://pypispy.com API.

"""
import json
import os
import subprocess
import traceback
import urllib
from datetime import datetime

import settings


class PyPiSpyAgent():
    def __init__(self, server_name, venvs, venvs_dir, email, api_key,
                 api_url=None):
        """
        Sets some class attributes for convenience.

        :param server_name: The SERVER_NAME setting.
        :param venvs: The VENVS setting.
        :param venvs_dir: The VENVS_DIR setting.
        :param email: The EMAIL setting.
        :param api_key: The API_KEY setting.
        :param api_url: The API_URL setting.

        """
        self.server_name = server_name
        self.venvs = venvs
        self.venvs_dir = venvs_dir
        self.email = email
        self.api_key = api_key
        self.api_url = api_url

    def handle_api_response(self, url, resp, raise_exception=True):
        if resp.code == 200:
            return resp

        if resp.code == 404:
            error = 'URL not found: %s' % url
            self.log_error(error)
            return resp

        if resp.code == 500:
            error = 'Server error'
            self.log_error(error)
            return resp

        if not raise_exception:
            error = resp.read()
            self.log_error(error)
            return resp

        error = json.loads(resp.read())
        raise Exception(error)

    def log_error(self, error):
        """
        Takes an error message as json string and writes it to the log together
        with additional information.

        """
        log_file = open('error.log', 'a')
        error_message = (str(datetime.now()) + ' ' +
            str(error) + '\n')
        log_file.write(error_message)

    def call_url(self, url, data):
        post_data = urllib.urlencode(data)
        return urllib.urlopen(url=url, data=post_data)

    def call_error_api(self, error, venv):
        """
        Calls an API at pypispy.com to log this error.

        This enables the pypispy team to proactively monitor errors that
        happen on client side and provide support as fast as possible.

        """
        url = '{0}error/'.format(self.api_url)
        post_data = {
            'date': str(datetime.now()),
            'user':  self.email,
            'api_key': self.api_key,
            'server_name': self.server_name,
            'venv_name': venv,
            'stack_trace': error
        }
        resp = self.call_url(url, post_data)
        return self.handle_api_response(url, resp, raise_exception=False)

    def call_pypispy_api(self, data, venv):
        """Posts the gathered data to the pypispy.com API"""
        url = '{0}venv/{1}/'.format(self.api_url, venv)
        resp = self.call_url(url, data)
        return self.handle_api_response(url, resp)

    def get_package_list(self, venv):
        """
        Activates the venv and creates a list of installed python packages.

        """
        # activate virtual environment
        activate_this = os.path.expanduser(
             os.path.join(self.venvs_dir, venv, 'bin/activate_this.py'))
        execfile(activate_this, dict(__file__=activate_this))

        # get installed packages
        package_list = subprocess.Popen(
            ['pip', 'freeze'],
            stdout=subprocess.PIPE).communicate()[0]
        return package_list

    def inspect_venv(self, venv):
        """
        Collects information on installed packages and sends them as
        JSON-String to the pypispy.com API.

        """
        package_list = self.get_package_list(venv)

        data = {
            'email': self.email,
            'api_key': self.api_key,
            'server_name': self.server_name,
            'package_info': package_list,
        }
        return data

    def run(self):
        """
        Iterates through all venvs and sends the package info to the
        pypispy.com API.

        """
        for venv in self.venvs:
            try:
                data = self.inspect_venv(venv)
                self.call_pypispy_api(data, venv=venv)
            except Exception, ex:
                tb = traceback.format_exc()
                self.log_error(ex)
                self.call_error_api(tb, venv)


if __name__ == "__main__":
    agent = PyPiSpyAgent(
        settings.SERVER_NAME,
        settings.VENVS,
        settings.VENVS_DIR,
        settings.EMAIL,
        settings.API_KEY,
        settings.API_URL,
    )
    agent.run()
