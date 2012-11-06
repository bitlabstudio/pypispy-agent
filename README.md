pyispy-agent
============

This script should be deployed by customers of https://pypispy.com

It iterates over the virtualenvs on the server and calls `pip freeze` for each
virtualenv. It sends the result as a JSON string to the https://pypispy.com API.

A user can then login to his account on https://pypispy.com and get an overview
of the package information on all his servers. We also send email notifications 
once a package gets out of date and a weekly digest of all outdated packages
on all servers.

Installation
------------

In order to install this script you need to do the following:

* Clone this script into a folder on your server.
* Copy `settings.py.sample` into `settings.py` and make your settings.
* Schedule the execution of this script via crontab, for example like so:
  `0 3 * * * /usr/local/bin/python2.7 $HOME/opt/pypispy_agent/pypispy.py > $HOME/logs/cron/pypispy.log 2>&1`

For more detailed instructions please create an account at https://pypispy.com
and visit our how-to page at https://pypispy.com/app/agent/
