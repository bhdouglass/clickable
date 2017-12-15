.. _usage:

Usage
=====

Getting Started
---------------

You can get started with using clickable with an existing Ubuntu Touch app.
You can use clickable with apps generated from the old Ubuntu Touch SDK IDE
or you can start fresh with `this app template <https://github.com/bhdouglass/ut-app-template>`__.

To run the default set of sub-commands, simply run ``clickable`` in the root directory
of your app's code. Clickable with attempt to auto detect the
:ref:`build template <build-templates>` and other configuration options,
if you need more advanced usage options read the
:ref:`clickable.json format guide <clickable-json>`.

Running the default sub-commands will:

1) Kill the running app on the phone
2) Clean the build directory (by default the build directory is ``./build/``)
3) Compile the app (if needed)
4) Build the click package (can be found in the build directory)
5) Install the app on your phone (By default this uses adb, see below if you want to use ssh)
6) Launch the app on your phone

Connecting to a device over ssh
-------------------------------

By default the device is connected to via adb.
If you want to access a device over ssh you need to either specify the device
IP address on the command line (ex: ``clickable logs --ip 192.168.1.10`` ) or you

Multiple connected devices
--------------------------

By default clickable assumes that there is only one device connected to your
computer via adb. If you have multiple devices attached to your computer you
can specify which device to install/launch/etc on by using the flag
``--device-serial-number`` or ``-s`` for short. You can get the serial number
by running ``adb devices``.
