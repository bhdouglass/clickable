# [Clickable](https://clickable-ut.dev/en/latest/)

Compile, build, and deploy Ubuntu Touch click packages all from the command line.

## Install

### Via Pip (Recommended)

* Install docker, adb, git, python3 and pip3
  (in Ubuntu: `sudo apt install docker.io adb git python3 python3-pip`)
* Run: `pip3 install --user --upgrade clickable-ut`
* Add pip scripts to your PATH: `echo 'export PATH="$PATH:~/.local/bin"' >> ~/.bashrc` and open a new terminal for the setting to take effect
* Alternatively, to install nightly builds: `pip3 install --user git+https://gitlab.com/clickable/clickable.git@dev`

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

- [Getting Started](https://clickable-ut.dev/en/latest/getting-started.html)
- [Usage](https://clickable-ut.dev/en/latest/usage.html)
- [Commands](https://clickable-ut.dev/en/latest/commands.html)
- [clickable.json Format](https://clickable-ut.dev/en/latest/clickable-json.html)
- [App Templates](https://clickable-ut.dev/en/latest/app-templates.html)
- [Builders](https://clickable-ut.dev/en/latest/builders.html)

## Code Editor Integrations

Use clickable with the [Atom Editor](https://atom.io) by installing [atom-clickable-plugin](https://atom.io/packages/atom-clickable-plugin).
This is an fork of the original (now unmaintained) [atom-build-clickable](https://atom.io/packages/atom-build-clickable)
made by Stefano.

## Development

### Run clickable

Best add your clickable folder to `PATH`, so you don't need to run the clickable commands from the repo root.
This can be done by adding `export PATH="$PATH:$HOME/clickable"` to your `.bashrc`.
Replace `$HOME/clickable` with your path.

To test clickable, run `clickable-dev`. Add the `--verbose` option for additional output.

To enable configuration validation either install **jsonschema** via pip
(`pip3 install jsonschema`) or apt (`apt install python3-jsonschema`). If you
got clickable regularly installed, you already have jsonschema, too.

### Run the tests

Install nose and the coverage modules: `pip3 install nose coverage`.

Run nose to complete the tests: `nosetests`.

### Related Repositories

* [Clickable docker images and app templates](https://gitlab.com/clickable)

## Donate

If you like Clickable, consider giving a small donation over at my
[Liberapay page](https://liberapay.com/bhdouglass).

## License

Copyright (C) 2020 [Brian Douglass](http://bhdouglass.com/)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License version 3, as published
by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranties of MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
