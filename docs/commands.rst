.. _commands:

Commands
========

From the root directory of your project you have the following sub-commands available:

You can combine the commands together like ``clickable build click_build install launch``

``clickable``

Runs the default sub-commands specified in the "default" config

``clickable kill``

Kills a running process (specified by the config). Using this you can relaunch your app.

``clickable clean``

Cleans out the build dir.

``clickable build``

Builds the project using the specified template, build dir, and build commands.

``clickable click-build``

Takes the built files and compiles them into a click package (you can find it in the build dir).

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

``clickable <custom command>``

Runs a custom command specified in the "scripts" config

``clickable <custom command> - -device``

Runs a custom command specified in the "scripts" config on the device.
