Clickable
=========

Compile, build, and deploy Ubuntu Touch click packages all from the command line.

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

Post Install
------------

Run ``clickable setup-docker`` to ensure that docker is configured for use with clickable.

Getting Started
---------------

To start a new project simply run ``clickable init`` and choose from the list of
:ref:`app templates <app-templates>`. When you have finished generating your app,
enter the newly created directory containing your app and run ``clickable``
to compile your app and install it on your phone.

For more information about the Ubuntu Touch QML or HTML SDK check out the
`docs over at UBports <https://api-docs.ubports.com>`__.

When you are ready to publish your app, head to the
`OpenStore's submission page <https://open.uappexplorer.com/submit>`__.

Issues and Feature Requests
---------------------------

If you run into any problems using clickable or have any feature requests you
can find clickable on `GitHub <https://github.com/bhdouglass/clickable/issues>`__.
