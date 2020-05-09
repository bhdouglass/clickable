.. _install:

Install
=======

Install Via Pip (Recommended)
-----------------------------

* Install docker, adb, git, python3 and pip3 
  (in Ubuntu: ``sudo apt install docker.io adb git python3 python3-pip``)
* Run (may need sudo): ``pip3 install clickable-ut``
* Add pip to your PATH: ``echo '[ -d ~/.local/bin ] export PATH=$PATH:~/.local/bin'`` and open a new terminal for the setting to take effect
* Alternatively, to install nightly builds: ``pip3 install git+https://gitlab.com/clickable/clickable.git@dev``

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

* Launch clickable and let it setup docker (it could ask for the sudo password): ``clickable``
* Log out or restart to apply changes
