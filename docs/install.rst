.. _install:

Install
=======

Install Via PPA (Ubuntu)
------------------------

* Add the PPA to your system: ``sudo add-apt-repository ppa:bhdouglass/clickable``
* Update your package list: ``sudo apt-get update``
* Install clickable: ``sudo apt-get install clickable``

Install Via Snap
----------------

* Make sure you have the dependencies ``adb`` and ``docker`` insalled
* Download the latest version from the `OpenStore <https://open.uappexplorer.com/snap/clickable>`__
* Install the snap: ``sudo snap install --force-dangerous --classic <path/to/snap>``

Post Install
------------

Run ``clickable setup-docker`` to ensure that docker is configured for use with clickable.
