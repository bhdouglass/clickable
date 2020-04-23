.. _getting-started:

Getting Started
===============

* Run ``clickable create`` to get started with a new app.
* Choose from the list of :ref:`app templates <app-templates>`.
* Provide all the needed information about your new app.
* When the app has finished generating, enter the newly created directory containing your app.
* Run ``clickable`` to compile your app and install it on your phone.

Getting Logs
------------

To get logs from your app simply run `clickable logs`. This will give you output
from C++ (``QDebug() << "message"``) or from QML (``console.log("message")``)
in addition to any errors or warnings.

Running on the Desktop
----------------------

Running the app on the desktop just requires you to run ``clickable desktop``.
This is not as complete as running the app on your phone, but it can help
speed up development.

Accessing Your Device
---------------------

If you need to access a terminal on your Ubuntu Touch device you can use
``clickable shell`` to open up a terminal to your device from your computer.
This is a replacement for the old ``phablet-shell`` command.

Ubuntu Touch SDK Api Docs
-------------------------

For more information about the Ubuntu Touch QML or HTML SDK check out the
`docs over at UBports <https://api-docs.ubports.com>`__.

Run Automatic Review
--------------------

Apps submitted to the OpenStore will undergo automatic review, to test your
app before submitting it, run ``clickable review`` after you've compiled a click.
This runs the ``click-review`` command against your click within the clickable
container (no need to install it on your computer).

.. _publishing:

Handling Dependencies
---------------------
For more information about compiling, using and deploying app dependencies, check out the
`docs over at UBports <https://docs.ubports.com/en/latest/appdev/guides/dependencies.html>`__.


Publishing to the OpenStore
---------------------------

If this is your first time publishing to the OpenStore, you need to
`signup for an account <https://open-store.io/login>`__. You can signup with
your GitHub, GitLab, or Ubuntu account.

If your app is new to the OpenStore you must first create your app by entering
the name from your manifest.json and the app's title
on the `OpenStore's submission page <https://open-store.io/submit>`__.

If your app already exists you can use the ``clickable publish`` command to
upload your compiled click file to the OpenStore. In order to publish to the
OpenStore you need to grab your
`api key from the OpenStore <https://open-store.io/manage>`__. After you have
your api key you need to let Clickable know about it. You can either pass it
as an argument every time: ``clickable publish --apikey XYZ`` Or you can set it
as an environment variable: ``export OPENSTORE_API_KEY=XYZ`` (you can add this
to your ``~/.bashrc`` to keep it set).
