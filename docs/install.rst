.. _install:

Install
=======

Install Via PPA (Ubuntu)
------------------------

* Add the `PPA <https://launchpad.net/~bhdouglass/+archive/ubuntu/clickable>`__ to your system: ``sudo add-apt-repository ppa:bhdouglass/clickable``
* Update your package list: ``sudo apt-get update``
* Install clickable: ``sudo apt-get install clickable``

Install Via Git
---------------

* Install `Docker <https://www.docker.com>`__
* Install `Cookiecutter <https://cookiecutter.readthedocs.io/en/latest/installation.html#install-cookiecutter>`__
* Clone this repo: ``git clone https://github.com/bhdouglass/clickable.git``
* Add clickable to your PATH: ``echo "export PATH=\$PATH:\$HOME/clickable" >> ~/.bashrc``
* Read the new ``.bashrc`` file: Run ``bash`` or open a new terminal window

Post Install
------------

Run ``clickable setup-docker`` to ensure that docker is configured for use with clickable.
