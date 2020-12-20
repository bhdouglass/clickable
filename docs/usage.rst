.. _usage:

Usage
=====

Getting Started
---------------

At this point it is assumed that you have completed the :ref:`installation
process <install>`

To find out all supported command line arguments run ``clickable --help``.

You can get started with using clickable with an existing Ubuntu Touch app.
You can use clickable with apps generated from the old Ubuntu Touch SDK IDE
or you can start fresh by running ``clickable create`` which is outlined in more
detail on the previous :ref:`getting started <getting-started>` page.

To run the default set of sub-commands, simply run ``clickable`` in the root directory
of your app's code. Clickable will attempt to auto detect the
:ref:`build template <builders>` and other configuration options.

Note: The first time you run ``clickable`` in your app directory, behind the
scenes it will download a new Docker container which is about 1GB in size - so
plan your time and data transfer environment accordingly. This will only happen
the first time you build your app for a specific architecture and when you run
``clickable update``.

Running the default sub-commands will:

1) Clean the build directory (by default ``./build/<arch_triplet>/app``)
2) Build the app
3) Build the click package (can be found in the build directory)
4) Install the app on your phone (By default this uses adb, see below if you want to use ssh)
5) Kill the running app on the phone
6) Launch the app on your phone

Note: ensure your device is in `developer mode <http://docs.ubports.com/en/latest/userguide/advanceduse/adb.html?highlight=mode#enable-developer-mode>`__
for the app to be installed when using adb or `enable ssh <http://docs.ubports.com/en/latest/userguide/advanceduse/ssh.html>`__
when using ssh.

Configuration
-------------
It is recommend to specify a configuration file in the
:ref:`clickable.json format <clickable-json>` with ``--config``. If not
specified, clickable will look for an optional configuration file called
``clickable.json`` in the current directory. If there is none Clickable will
ask if it should attempt to detect the type of app and choose a fitting
:ref:`builder <builders>` with default configuration.

.. _ssh:

Connecting to a device over ssh
-------------------------------

By default the device is connected to via adb.
If you want to access a device over ssh you need to either specify the device
IP address or hostname on the command line (ex: ``clickable logs --ssh 192.168.1.10`` ) or you
can use the ``CLICKABLE_SSH`` env var. Make sure to `enable ssh <http://docs.ubports.com/en/latest/userguide/advanceduse/ssh.html>`__
on your device for this to work.

.. _multiple-devices:

Multiple connected devices
--------------------------

By default clickable assumes that there is only one device connected to your
computer via adb. If you have multiple devices attached to your computer you
can specify which device to install/launch/etc on by using the flag
``--serial-number`` or ``-s`` for short. You can get the serial number
by running ``clickable devices``.

App Manifest
------------

The ``architecture`` and ``framework`` fields in the ``manifest.json`` need to be set according
to the architecture the app is build for (``--arch``) and the minimum framework version it
requires, e.g. depending on the QT Version (:ref:`qt_version <clickable-json-qt_version>`).
To let Clickable automatically set those fields, leave them empty or set them to
``@CLICK_ARCH@`` and ``@CLICK_FRAMEWORK@`` respectively.

Note: The app templates provided by Clickable make use of CMake's ``configure()`` to set
the fields in the ``manifest.json``.

Advanced Usage
--------------

.. _lxd:

Running Clickable in an LXD container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to run ``clickable`` in a container itself, using ``lxd``. This is not using ``--container-mode``, but allowing ``clickable`` to create docker containers as normal, but inside the existing ``lxd`` container. This may fail with a permissions error when mounting ``/proc``:

.. code-block:: bash

   docker: Error response from daemon: OCI runtime create failed: container_linux.go:349: starting container process caused "process_linux.go:449: container init caused \"rootfs_linux.go:58: mounting \\\"proc\\\" to rootfs \\\"/var/lib/docker/vfs/dir/bffeb203fe06662876a521b1bea3b74e4d5c6ea3535352215c199c75836aa925\\\" at \\\"/proc\\\" caused \\\"permission denied\\\"\"": unknown.

If this error occurs then ``lxd`` needs to be `configured to allow nested containers <https://stackoverflow.com/questions/46645910/docker-rootfs-linux-go-permission-denied-when-mounting-proc>` on the host:

.. code-block:: bash

   lxc stop your-container-name
   lxc config set your-container-name security.nesting true
   lxc start your-container-name
