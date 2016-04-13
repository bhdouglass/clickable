# Clickable

Compile, build, and deploy Ubuntu Touch click packages all from the command line.

## Usage

1) Put the `clickable` file on your PATH somewhere and make it executable

2) Create a `clickable.json` file in your project root with the contents:

```
{
  "package": "full package name (appname.developer) [Required]",
  "app": "app name (for auto launch) [Required]",
  "sdk": "ubuntu-sdk-15.04 [Required]",
  "arch": "armhf [Required]",
  "prebuild": "custom prebuild command [Optional]",
  "template": "pure-qml-qmake,qmake,pure-qml-cmake,cmake,custom [Required]",
  "premake": "custom command before make is run [Optional]",
  "build": "custom build command [Required if using custom template]",
  "postbuild": "custom command for after build, pre click build [Optional]",
  "launch": "custom launch command [Optional]",
  "ssh": "IP of device to install to (if not using phablet-shell) [Optional]",
  "dir": "./path/to/build/dir/ [Required]"
}
```

3) From the root directory of your project you have the following commands available:

* `clickable build` - Builds the project using the specified template, build dir, and build commands
* `clickable click_build` - Takes the built files and compiles them into a click package (you can find it in the build dir)
* `clickable install` - Takes a built click package and installs it on a device
* `clickable launch` - Launches the app on a device

You can combine the commands together like `clickable build click_build install launch`

## Templates

* `pure-qml-qmake` - A purely qml qmake project
* `qmake` - A project that builds using qmake (has more than just QML)
* `pure-qml-cmake` - A purely qml cmake project
* `cmake` - A project that builds using cmake (has more than just QML)
* `custom` - The custom build command will be used

## License

Copyright (C) 2016 [Brian Douglass](http://bhdouglass.com/)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License version 3, as published
by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranties of MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
