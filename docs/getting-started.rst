Getting Started
===============

* Run ``clickable init`` to get started with a new app.
* Choose from the list of :ref:`app templates <app-templates>`.
* Provide all the needed information about your new app.
* When the app has finished generating, enter the newly created directory containing your app.
* Run ``clickable`` to compile your app and install it on your phone.

Getting Logs
------------

To get logs from you app simply run `clickable logs`. This will give you output
from C++ (``QDebug() << "message"``) or from QML (``console.log("message")``)
in addition to any errors or warnings.

Running on the Desktop
----------------------

Running the app on the desktop just requires you to run ``clickable --desktop``.
This is not as complete as running the app on your phone, but it can help
speed up development.

Ubuntu Touch SDK Api Docs
-------------------------

For more information about the Ubuntu Touch QML or HTML SDK check out the
`docs over at UBports <https://api-docs.ubports.com>`__.

Submitting to the OpenStore
---------------------------

When you are ready to publish your app, head to the
`OpenStore's submission page <https://open.uappexplorer.com/submit>`__.
