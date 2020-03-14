Clickable
=========

Build and compile Ubuntu Touch apps easily from the command line. Deploy your
apps to your Ubuntu Touch device for testing or test them on any desktop Linux
distribution. Get logs for debugging and directly access a terminal on your device.

Clickable is fully Open Source and can be found on `GitLab <https://gitlab.com/clickable/clickable>`__.
Clickable is developed by `Brian Douglass <http://bhdouglass.com>`__ and
`Jonatan Hatakeyama Zeidler <https://gitlab.com/jonnius>`__ with a huge
thank you to all the `contributors <https://gitlab.com/clickable/clickable/graphs/master>`__.

Using Clickable
---------------

.. toctree::
    :maxdepth: 1
    :name: clickable

    install
    getting-started
    usage
    debugging
    commands
    clickable-json
    env-vars
    app-templates
    build-templates
    continuous-integration
    changelog

Install Via Pip (Recommended)
-----------------------------

* Install docker, adb, and pip3
* Run (may need sudo): ``pip3 install git+https://gitlab.com/clickable/clickable.git``

Install Via PPA (Ubuntu)
------------------------

* Add the `PPA <https://launchpad.net/~bhdouglass/+archive/ubuntu/clickable>`__ to your system: ``sudo add-apt-repository ppa:bhdouglass/clickable``
* Update your package list: ``sudo apt-get update``
* Install clickable: ``sudo apt-get install clickable``


Install Via AUR (Arch Linux)
----------------------------

* Using your favorite AUR helper, install the `clickable-git package <https://aur.archlinux.org/packages/clickable-git/>`__
* Example: ``pacaur -S clickable-git``

Getting Started
---------------

:ref:`Read the getting started guide to get started developing with clickable. <getting-started>`

Code Editor Integrations
------------------------

Use clickable with the `Atom Editor <https://atom.io>`__ by installing
`atom-build-clickable <https://atom.io/packages/atom-build-clickable>`__
made by Stefano.

Issues and Feature Requests
---------------------------

If you run into any problems using clickable or have any feature requests you
can find clickable on `GitLab <https://gitlab.com/clickable/clickable/issues>`__.
