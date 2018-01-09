Clickable
=========

Build and compile Ubuntu Touch apps easily from the command line. Deploy your
apps to your Ubuntu Touch device for testing or test them on any desktop Linux
distribution. Get logs for debugging and directly access a terminal on your device.

Clickable is fully Open Source and can be found on `GitHub <https://github.com/bhdouglass/clickable>`__.
Clickable is developed by `Brian Douglass <http://bhdouglass.com>`__ with a huge
thank you to all the `contributors <https://github.com/bhdouglass/clickable/graphs/contributors>`__.

Using Clickable
---------------

.. toctree::
    :maxdepth: 1
    :name: clickable

    install
    getting-started
    usage
    commands
    clickable-json
    app-templates
    build-templates

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
* Add clickable to your PATH: ``PATH=$PATH:/path/to/clickable`` (It is recommended to save this to your ``~/.bashrc``)

Post Install
------------

Run ``clickable setup-docker`` to ensure that docker is configured for use with clickable.

Getting Started
---------------

:ref:`Read the getting started guide to get started developing with clickable. <getting-started>`

Issues and Feature Requests
---------------------------

If you run into any problems using clickable or have any feature requests you
can find clickable on `GitHub <https://github.com/bhdouglass/clickable/issues>`__.
