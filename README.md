# Clickable

Compile, build, and deploy Ubuntu Touch click packages all from the command line.

## Install

For a great tutorial on how to get started with clickable, check out the one in the
[UBports Wiki](https://wiki.ubports.com/wiki/Set-up-an-app-development-environment).

### Prerequisites

* `adb` For installing and running commands on your device
* `lxd` For building any binaries and the click package
    * After installing lxd make sure you run `lxd init`

### Via Snap

* Download the latest version from the OpenStore: <https://open.uappexplorer.com/snap/clickable>
* Install the snap: `sudo snap install --force-dangerous --classic <path/to/snap>`

### Via Git

* Clone this repo: `git clone https://github.com/bhdouglass/clickable.git`
* Set the repo on your `PATH`

### Post Setup

Run `clickable setup-lxd` to create a container to build clicks and binaries in.

## Usage

1) Create a `clickable.json` file in your project root with the contents:

```
{
  "package": "full package name (appname.developer) [Optional, will be read from manifest.json if left blank]",
  "app": "app name (for auto launch) [Optional, will be read from manifest.json if left blank]",
  "sdk": "ubuntu-sdk-15.04 [Optional]",
  "arch": "armhf [Optional, default is armhf, or specify as a cli arg (ex: --arch="armhf")]",
  "prebuild": "custom prebuild command [Optional]",
  "template": "pure-qml-qmake,qmake,pure-qml-cmake,cmake,custom,cordova,pure [Required if not specified as a cli arg (ex: --template="cmake")]",
  "premake": "custom command before make is run [Optional]",
  "build": "custom build command [Required if using custom template]",
  "postbuild": "custom command for after build, pre click build [Optional]",
  "launch": "custom launch command [Optional]",
  "ssh": "IP of device to install to (if not using phablet-shell) [Optional]",
  "dir": "./path/to/build/dir/ [Optional, default is ./build/]",
  "kill": "Name of the process to kill (useful for killing the running app, then relaunching it) [Optional, if not specified it will be assumed]",
  "scripts": "An object that lists custom scripts to run, see below for more details",
  "chroot": "Whether or not to use a chroot (default is False, which means use an lxd container) [Optional]",
  "default": "A list of space separated sub-commands to run when no sub-commands are specified",
  "dependencies": "An array of dependencies that will be installed in the build container",
  "ignore": "An array of files to ignore when building a 'pure' template [Optional, only for pure templates]",
  "make_jobs": "number of jobs to use when running make, equivalent to make's -j option [Optional, if missing `make -j` will be run]",
}
```

2) From the root directory of your project you have the following sub-commands available:

* `clickable kill` - Kills a running process (specified by the config). Using this you can relaunch your app.
* `clickable clean` - Cleans out the build dir
* `clickable build` - Builds the project using the specified template, build dir, and build commands
* `clickable click-build` - Takes the built files and compiles them into a click package (you can find it in the build dir)
* `clickable install` - Takes a built click package and installs it on a device
* `clickable launch` - Launches the app on a device
* `clickable logs` - Follow the apps logfile on the device
* `clickable setup-lxd` - Setup an lxd container for building in
* `clickable <custom command>` - Runs a custom command specified in the "scripts" config
* `clickable <custom command> --device` - Runs a custom command specified in the "scripts" config on the device
* `clickable` - Runs the default sub-commands specified in the "default" config

You can combine the commands together like `clickable build click_build install launch`

## Connecting to a device over ssh

By default the device is connected to via adb and phablet-shell.
If you want to access a device over ssh you need to either specify the device
IP address on the command line (ex: `clickable logs --ip 192.168.1.10`) or you
can specify the IP address in the clickable.json file's `ssh` property.

## LXD Container Building

Clickable supports building in a lxd container. In order to use them you first
need to setup a container using `clickable setup-lxd` (once for each target architecture).
This requires that you have `usdk-target` command installed. If you have the Ubuntu
SDK IDE installed you may already have this command installed, but the version
included in this repo is more up to date than the Ubuntu SDK IDE verion. If
you are not running Ubuntu or do not already have the SDK IDE setup you will
need to use the usdk-target binary included in this repo.

## Chroot Building

Clickable supports the legacy chroots for building apps. In order to use them just
specify `"chroot": true` in your clickable.json. This requires that you already
have a chroot setup (via `click chroot create...`).

## Templates

* `pure-qml-qmake` - A purely qml qmake project
* `qmake` - A project that builds using qmake (has more than just QML)
* `pure-qml-cmake` - A purely qml cmake project
* `cmake` - A project that builds using cmake (has more than just QML)
* `custom` - The custom build command will be used
* `cordova` - A project that builds using cordova
* `pure` - A project that does not need to be compiled. All files in the project root will be copied into the click

## License

Copyright (C) 2016 [Brian Douglass](http://bhdouglass.com/)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License version 3, as published
by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranties of MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
