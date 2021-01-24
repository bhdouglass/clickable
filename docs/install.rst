.. _install:

Install
=======

Install Via Pip (Recommended)
-----------------------------

* Install docker, adb, git, python3 and pip3
  (in Ubuntu: ``sudo apt install docker.io adb git python3 python3-pip python3-setuptools``)
* Run: ``pip3 install --user clickable-ut``
* Add pip scripts to your PATH: ``echo 'export PATH="$PATH:~/.local/bin"' >> ~/.bashrc`` and open a new terminal for the setting to take effect
* Alternatively, to install nightly builds: ``pip3 install --user git+https://gitlab.com/clickable/clickable.git@dev``

To update Clickable via pip, run the same command as for installing, adding ``--upgrade``.

Install Via PPA (Ubuntu)
------------------------

* Add the `PPA <https://launchpad.net/~bhdouglass/+archive/ubuntu/clickable>`__ to your system: ``sudo add-apt-repository ppa:bhdouglass/clickable``
* Update your package list: ``sudo apt-get update``
* Install clickable: ``sudo apt-get install clickable``

Install Via AUR (Arch Linux)
----------------------------

* Using your favorite AUR helper, install the `clickable-git package <https://aur.archlinux.org/packages/clickable-git/>`__
* Example: ``pacaur -S clickable-git``

After install
=============

* Let Clickable setup docker (it could ask for the sudo password): ``clickable setup``
* Log out or restart to apply changes
