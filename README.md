# Clickable

Compile, build, and deploy Ubuntu Touch click packages all from the command line.

## Install

### Via Pip (Recommended)

* Install docker, adb, and pip3:
  * On Ubuntu: `sudo apt-get install docker.io adb python3-pip`
* Run (may need sudo): `pip3 install git+https://gitlab.com/clickable/clickable.git`

### Via PPA (Ubuntu)

* Add the PPA to your system: `sudo add-apt-repository ppa:bhdouglass/clickable`
* Update your package list: `sudo apt-get update`
* Install clickable: `sudo apt-get install clickable`

### Via AUR (Arch Linux)

* Using your favorite AUR helper, install the [clickable package](https://aur.archlinux.org/packages/clickable/)
* Example: `pacaur -S clickable

## After install

* Launch clickable and let it setup docker (it could ask for the sudo password): `clickable`
* Log out or restart to apply changes

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

### Run clickable

To test clickable, run `clickable-dev` from the repository root directory. To
enable configuration validation either install **jsonschema** via pip 
(`pip3 install jsonschema`) or apt (`apt install python3-jsonschema`). If you
got clickable regularly installed, you already have jsonschema, too.

### Run the tests

Install nose and the coverage modules: `pip3 install nose coverage`

Run nose to complete the tests: `nosetests`

### Related Repositories

* [Clickable docker images and app templates](https://gitlab.com/clickable)

## Donate

If you like Clickable, consider giving a small donation over at my
[Liberapay page](https://liberapay.com/bhdouglass).

## License

Copyright (C) 2018 [Brian Douglass](http://bhdouglass.com/)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License version 3, as published
by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranties of MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
