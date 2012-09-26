pyispy-agent
============

This script should be deployed by customers of http://pypispy.com

It iterates over the virtualenvs on the server and calls `pip freeze` for each
venv. It sends the result as a JSON string to the pypispy.com API.

As a result a user can login to his account on pypispy.com and get an overview
over the package information on all his servers. We also send email
notifications once a package gets out of date.

TODO: Describe how to install and schedule this script via crontab.

TODO: Describe how to contribute to this script.
