.. _changelog:

Changelog
=========

Chagnes in v5.12.0
------------------

- clickable.json supports :ref:`placeholders <clickable-json-placeholders>` now
- Add new ``src_dir`` configuration option
- Make build-libs respect ``root_dir``, too
- Fix build-libs for architecture all
- When no ``kill`` configuration option is specified Clickable will use the Exec line from the desktop file

Changes in v5.11.0
------------------

- Smarter app killing using ``pkill -f``
- Fix deprecated configuration options showing as a schema error

Changes in v5.10.0
------------------

- Added configuration option ``root_dir``
- Always ignore .git/.bzr directories when building pure, rust, or go apps

Changes in v5.9.1
-----------------

- Fixed missing schema file

Changes in v5.9.0
-----------------

- New schema validation for clickable.json
- Publish to the OpenStore with a changelog message

Changes in v5.8.1
-----------------

- Fixed a bug in ``make_args``

Changes in v5.8.0
-----------------

- New configuration option for automatically including ppas in the build environment: :ref:`dependencies_ppa <clickable-json-dependencies-ppa>`.
- Changed :ref:`libraries <clickable-json-libraries>` format from a list to a dictionary (the old format is still supported for now)
- The default ``cargo_home`` is now set to ``~/.cargo``

Changes in v5.7.0
-----------------

- Introduced two new dependency options to separate `build <clickable-json-dependencies_build>` and `target <clickable-json-dependencies_target>` dependencies

Changes in v5.6.1
-----------------

- Fixed build lib
- Made cordova build respect the --debug-build argument

Changes in v5.6.0
-----------------

- Fixed Cordova build
- Added ``--debug-build`` support for QMake and CMake templates

Changes in v5.5.1
-----------------

- New ``--config`` argument to specify a different path to the clickable.json file
- New configuration called ``clickable_minimum_required`` to specify a minimum version of Clickable
- New ``make_args`` configuration for passing arguments to make

Changes in v5.5.0
-----------------

- build-libs now only uses the same arch as specified in clickable.json or in the cli args
- Added the option to build/clean only one lib
- Added support for GOPATH being a list of paths
- Exits with an error with an invalid command

Changes in v5.4.0
-----------------

- Added support for Rust apps
- Added support for distros using SELinux

Changes in v5.3.3
-----------------

- More fixes for building libraries
- Set the home directory to /home/phablet in desktop mode

Changes in v5.3.2
-----------------

- Fixed issue building libraries
- Create arch specific directories in .clickable
- Fixed --dirty breaking when using a custom default set of commands

Changes in v5.3.1
-----------------

- Fixed dependencies in library prebuild

Changes in v5.3.0
-----------------

- :ref:`Added options for compiling libraries <clickable-json-libraries>`

Changes in v5.2.0
-----------------

- Fixed bug in build template auto detection
- Added new dirty build option

Changes in v5.1.1
-----------------

- Fixed bug in "shell" command

Changes in v5.1.0
-----------------

- Added app template for QML/C++ with a main.cpp

Changes in v5.0.2
-----------------

- Fixed publish command not exiting with an error code when there is an error

Changes in v5.0.1
-----------------

- Fixed typo in cache path
- Improved Cordova support

Changes in v5.0.0
-----------------

- New features
    - Xenial by default (use ``--vivid`` to compile for 15.04)
    - Major code refactor
    - More environment variables
        - ``CLICKABLE_ARCH`` - Overrides the clickable.json's ``arch``
        - ``CLICKABLE_TEMPLATE`` - Overrides the clickable.json's ``template``
        - ``CLICKABLE_DIR`` - Overrides the clickable.json's ``dir``
        - ``CLICKABLE_LXD`` - Overrides the clickable.json's ``lxd``
        - ``CLICKABLE_DEFAULT`` - Overrides the clickable.json's ``default``
        - ``CLICKABLE_MAKE_JOBS`` - Overrides the clickable.json's ``make_jobs``
        - ``GOPATH`` - Overrides the clickable.json's ``gopath``
        - ``CLICKABLE_DOCKER_IMAGE`` - Overrides the clickable.json's ``docker_image``
        - ``CLICKABLE_BUILD_ARGS`` - Overrides the clickable.json's ``build_args``
        - ``OPENSTORE_API_KEY`` - Your api key for publishing to the OpenStore
        - ``CLICKABLE_CONTAINER_MODE`` - Same as ``--container-mode``
        - ``CLICKABLE_SERIAL_NUMBER`` - Same as ``--serial-number``
        - ``CLICKABLE_SSH`` - Same as ``--ssh``
        - ``CLICKABLE_OUTPUT`` - Override the output directory for the resulting click file
        - ``CLICKABLE_NVIDIA`` - Same as ``--nvidia``
        - ``CLICKABLE_VIVID`` - Same as ``--vivid``
- Removed
    - Chroot support has been removed, docker containers are recommended going forward
- clickable.json
    - Removed
        - ``package`` - automatically grabbed from the manifest.json
        - ``app`` - automatically grabbed from the manifest.json
        - ``sdk`` - Replaced by docker_image and the ``--vivid`` argument
        - ``premake`` - Use ``prebuild``
        - ``ssh`` - Use the ``--ssh`` argument
- Commands
    - New
        - ``log`` - Dumps the full log file from the app
        - ``desktop`` - Replaces ``--desktop`` to run the app in desktop mode
    - Changed
        - ``init`` - Changed to ``create`` (``init`` will still work)
        - ``update-docker`` - Changed to ``update``
    - Removed
        - ``kill`` - Changed to be part of the ``launch`` command
        - ``setup-docker`` - Automatically detected and run when using docker
        - ``display-on`` - Not very useful
- Command line arguments
    - New
        - ``--vivid`` - Compile the app for 15.04
        - ``--docker-image`` - Compile the app using a specific docker image
    - Changed
        - ``--serial-number`` - Replaces ``--device-serial-number``
        - ``--ssh`` - Replaces ``--ip``
    - Removed
        - ``--desktop`` - Use the new ``desktop`` command
        - ``--xenial`` - Xenial is now the default
        - ``--sdk`` - Use ``--vivid`` or ``--docker-image``
        - ``--device`` - Use ``shell``
        - ``--template`` - Use the ``CLICKABLE_TEMPLATE`` env var
        - ``--click`` - Specify the path to the click after the ``install`` command: ``clickable install /path/to/click``
        - ``--app`` - Specify the app name after the ``launch`` command: ``clickable launch app.name``
        - ``--name`` - Specify the app template after the ``create`` command: ``clickable create pure-qml-cmake``
