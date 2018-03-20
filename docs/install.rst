.. _install:

Install
=======

Install Via PPA (Ubuntu)
------------------------

* Add the `PPA <https://launchpad.net/~bhdouglass/+archive/ubuntu/clickable>`__ to your system: ``sudo add-apt-repository ppa:bhdouglass/clickable``
* Update your package list: ``sudo apt-get update``
* Install clickable: ``sudo apt-get install clickable``
* Configure docker for clickable: ``clickable setup-docker``

Install Via AUR (Arch Linux)
----------------------------

* Using your favorite AUR helper, install the `clickable package <https://aur.archlinux.org/packages/clickable/>`__
* Example: ``pacaur -S clickable``

Install Via Git
---------------

* Install `Docker <https://www.docker.com>`__
* Install `Cookiecutter <https://cookiecutter.readthedocs.io/en/latest/installation.html#install-cookiecutter>`__
* Clone this repo: ``git clone https://github.com/bhdouglass/clickable.git``
* Add clickable to your PATH: ``echo "export PATH=\$PATH:\$HOME/clickable" >> ~/.bashrc``
* Read the new ``.bashrc`` file: ``source ~/.bashrc``
* Configure docker for clickable: ``clickable setup-docker``
