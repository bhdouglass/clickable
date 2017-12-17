# Clickable

Compile, build, and deploy Ubuntu Touch click packages all from the command line.

## Install

### Via PPA (Ubuntu)

* Add the PPA to your system: `sudo add-apt-repository ppa:bhdouglass/clickable`
* Update your package list: `sudo apt-get update`
* Install clickable: `sudo apt-get install clickable`

### Via Snap

* Make sure you have the dependencies `adb` and `docker` insalled
* Download the latest version from the OpenStore: <https://open.uappexplorer.com/snap/clickable>
* Install the snap: `sudo snap install --force-dangerous --classic <path/to/snap>`

### Post Setup

Run `clickable setup-docker` to ensure that docker is configured for use with clickable.

## Docs

- [Usage](http://clickable.bhdouglass.com/en/latest/usage.html)
- [Install](http://clickable.bhdouglass.com/en/latest/install.html)
- [Commands](http://clickable.bhdouglass.com/en/latest/commands.html)
- [clickable.json Format](http://clickable.bhdouglass.com/en/latest/clickable-json.html)
- [Build Templates](http://clickable.bhdouglass.com/en/latest/build-templates.html)

## License

Copyright (C) 2017 [Brian Douglass](http://bhdouglass.com/)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License version 3, as published
by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranties of MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
