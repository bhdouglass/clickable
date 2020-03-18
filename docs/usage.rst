.. _usage:

Usage
=====

Getting Started
---------------

You can get started with using clickable with an existing Ubuntu Touch app.
You can use clickable with apps generated from the old Ubuntu Touch SDK IDE
or you can start fresh by running ``clickable create``.

To run the default set of sub-commands, simply run ``clickable`` in the root directory
of your app's code. Clickable will attempt to auto detect the
:ref:`build template <build-templates>` and other configuration options.

Running the default sub-commands will:

1) Clean the build directory (by default the build directory is ``./build/``)
2) Compile the app
3) Build the click package (can be found in the build directory)
4) Install the app on your phone (By default this uses adb, see below if you want to use ssh)
5) Kill the running app on the phone
6) Launch the app on your phone

Configuration
-------------
If you need more advanced usage options, you may specify a configuration file
in the :ref:`clickable.json format <clickable-json>` with ``--config``. If not
specified, clickable will look for an optional configuration file called
``clickable.json`` in the current directory.

.. _ssh:

Connecting to a device over ssh
-------------------------------

By default the device is connected to via adb.
If you want to access a device over ssh you need to either specify the device
IP address or hostname on the command line (ex: ``clickable logs --ssh 192.168.1.10`` ) or you
can use the ``CLICKABLE_SSH`` env var.

.. _multiple-devices:

Multiple connected devices
--------------------------

By default clickable assumes that there is only one device connected to your
computer via adb. If you have multiple devices attached to your computer you
can specify which device to install/launch/etc on by using the flag
``--serial-number`` or ``-s`` for short. You can get the serial number
by running ``clickable devices``.