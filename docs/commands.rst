.. _commands:

Commands
========

From the root directory of your project you have the following sub-commands available:

You can combine the commands together like ``clickable build click_build install launch``

``clickable``

Runs the default sub-commands specified in the "default" config

``clickable shell``

Opens a shell on the device via ssh. This is similar to the ``phablet-shell`` command.

``clickable kill``

Kills a running process (specified by the config). Using this you can relaunch your app.

``clickable clean``

Cleans out the build dir.

``clickable build``

Builds the project using the specified template, build dir, and build commands.

``clickable click-build``

Takes the built files and compiles them into a click package (you can find it in the build dir).

``clickable click-build --output=/path/to/some/diretory``

Takes the built files and compiles them into a click package, outputting the
compiled click to the directory specified by ``--output``.

``clickable install``

Takes a built click package and installs it on a device.

``clickable install --click ./path/to/click/app.click``

Installs the specified click package on the device

``clickable launch``

Launches the app on a device.

``clickable launch --app <app name>``

Launches the specified app on a device.

``clickable logs``

Follow the apps log file on the device.

``clickable setup-docker``

Configure docker for use with clickable.

``clickable display-on``

Turns on the device's display and keeps it on until you hit CTRL+C.

``clickable no-lock``

Turns off the device's display timeout.

``clickable devices``

Lists the serial numbers and model names for attached devices. Useful when
multiple devices are attached and you need to know what to use for the ``-s``
argument.

``clickable <custom command>``

Runs a custom command specified in the "scripts" config

``clickable <custom command> --device``

Runs a custom command specified in the "scripts" config on the device.

``clickable <any command> --container-mode``

Runs all builds commands on the current machine and not in a container. This is
useful from running clickable from within a container.
