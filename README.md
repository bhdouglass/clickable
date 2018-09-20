# Clickable

Compile, build, and deploy Ubuntu Touch click packages all from the command line.

## Install

### Via PPA (Ubuntu)

* Add the PPA to your system: `sudo add-apt-repository ppa:bhdouglass/clickable`
* Update your package list: `sudo apt-get update`
* Install clickable: `sudo apt-get install clickable`
* Configure docker for clickable: `clickable setup-docker`

### Via AUR (Arch Linux)

* Using your favorite AUR helper, install the [clickable package](https://aur.archlinux.org/packages/clickable/)
* Example: `pacaur -S clickable`

### Via Pip && Git

* Install [Docker](https://www.docker.com)
* Install: `sudo apt-get install python3-pip`
* Run: `sudo pip3 install git+https://github.com/bhdouglass/clickable.git`

### Post Setup

Run `clickable setup-docker` to ensure that docker is configured for use with clickable.
* Configure docker for clickable: `clickable setup-docker`

## Docs

- [Getting Started](http://clickable.bhdouglass.com/en/latest/getting-started.html)
- [Usage](http://clickable.bhdouglass.com/en/latest/usage.html)
- [Commands](http://clickable.bhdouglass.com/en/latest/commands.html)
- [clickable.json Format](http://clickable.bhdouglass.com/en/latest/clickable-json.html)
- [App Templates](http://clickable.bhdouglass.com/en/latest/app-templates.html)
- [Build Templates](http://clickable.bhdouglass.com/en/latest/build-templates.html)

## Code Editor Integrations

Use clickable with the [Atom Editor](https://atom.io) by installing
[atom-build-clickable](https://atom.io/packages/atom-build-clickable)
made by Stefano.

## Development

### Run the tests

Install nose and the coverage modules: `pip3 install nose coverage`

Run nose to complete the tests: `nosetests`

## License

Copyright (C) 2018 [Brian Douglass](http://bhdouglass.com/)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License version 3, as published
by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranties of MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
