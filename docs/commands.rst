.. _commands:

Commands
========

From the root directory of your project you have the following sub-commands available:

You can combine the commands together like ``clickable build click-build install launch``

``clickable``
-------------

Runs the default sub-commands specified in the "default" config. A dirty build
without cleaning the build dir can be achieved by running 
``clickable --dirty``.

``clickable desktop``
---------------------

Compile and run the app on the desktop.

Note: ArchLinux user might need to run ``xhost +local:clickable`` before using
desktop mode.

``clickable create``
------------------

Generate a new app from a list of :ref:`app template options <app-templates>`.

``clickable create <app template name>``

Generate a new app from an :ref:`app template <app-templates>` by name.

``clickable shell``
-------------------

Opens a shell on the device via ssh. This is similar to the ``phablet-shell`` command.

``clickable clean``
-------------------

Cleans out the build dir.

``clickable build``
-------------------

Builds the project using the specified template, build dir, and build commands.

``clickable click-build``
-------------------------

Takes the built files and compiles them into a click package (you can find it in the build dir).

``clickable click-build --output=/path/to/some/diretory``

Takes the built files and compiles them into a click package, outputting the
compiled click to the directory specified by ``--output``.

``clickable review``
--------------------

Takes the built click package and runs click-review against it. This allows you
to review your click without installing click-review on your computer.

``clickable install``
---------------------

Takes a built click package and installs it on a device.

``clickable install --click ./path/to/click/app.click``

Installs the specified click package on the device

``clickable launch``
--------------------

Launches the app on a device.

``clickable launch <app name>``

Launches the specified app on a device.

``clickable logs``
------------------

Follow the apps log file on the device.

``clickable log``
------------------

Dumps the apps log file on the device.

``clickable publish``
---------------------

Publish your click app to the OpenStore. Check the
:ref:`Getting started doc <getting-started>` for more info.

``clickable run "some command"``
--------------------------------

Runs an arbitrary command in the clickable container.

``clickable update``
---------------------------

Update the docker container for use with clickable.

``clickable no-lock``
---------------------

Turns off the device's display timeout.

``clickable writable-image``
----------------------------

Make your Ubuntu Touch device's rootfs writable. This replaces to old
``phablet-config writable-image`` command.

``clickable devices``
---------------------

Lists the serial numbers and model names for attached devices. Useful when
multiple devices are attached and you need to know what to use for the ``-s``
argument.

``clickable <custom command>``
------------------------------

Runs a custom command specified in the "scripts" config

.. _container-mode:

``clickable <any command> --container-mode``
--------------------------------------------

Runs all builds commands on the current machine and not in a container. This is
useful from running clickable from within a container.

.. _nvidia:

``clickable desktop --nvidia``
------------------------------

Use clickable's desktop mode with proprietary Nvidia drivers. This requires
nvidia-docker to be installed and setup. Please note, only version 1 of
nvidia-docker is supported at this time (version 2 does not support OpenGL).
