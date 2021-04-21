.. _changelog:

Changelog
=========

Changes in v6.24.1
------------------

- Fixed qmake building a pure qml app

Changes in v6.24.0
------------------

- Switched to use Qt 5.12 by default

Changes in v6.23.3
------------------

- When using the qmake builder a specific .pro file can be specified using the ``build_args`` setting
- Fixed cross-compiling for armhf with qmake when using Qt 5.12

Changes in v6.23.2
------------------

- Fixed version checker
- Fixed image update

Changes in v6.23.1
------------------

- Improved the Qt 5.9 docker images
- Rebuild docker images if the base image changes

Changes in v6.23.0
------------------

- Added new test-libs command to run tests on libs
- When using the verbosity flag make commands will also be verbose
- Fixed Qt version to Ubuntu framework mapping
- Added new version checker

Changes in v6.22.0
------------------

- Added more docs and improved error messages
- Added checks to avoid removing sources based on configuration
- Added support for building against Qt 5.12 or Qt 5.9
- Fixed rust problem when using nvidia

Changes in v6.21.0
------------------

- Added option to use an nvidia specific container for Clickable's ide feature
- Improved error messages when no device can be found
- Added option to set custom env vars for the build container via env vars provided to Clickable
- Improved how container version numbers are checked
- Improved checking for container updates
- Minor fixes

Changes in v6.20.1
------------------

- Fixed building libraries using make

Changes in v6.20.0
------------------

- Added support for armhf and arm64 hosts with new docker images
- Added support for env vars in image setup

Changes in v6.19.0
------------------

- Click review is now run after each build by default
- Added NUM_PROCS env var and placeholder for use in custom builders
- Enabled dependencies_ppa and image_setup in container mode
- Fixed issues detecting the timezone for desktop mode

Changes in v6.18.0
------------------

- Updated the ``clickable run`` command to use the container's root user

Changes in v6.17.1
------------------

- Fixed container mode when building libraries
- Added better handling of keyboard interrupts

Changes in v6.17.0
------------------

- Fixed errors when using ssh for some functions
- Added initial non-interactive mode to create new apps
- Added better error handling
- Allow opening qtcreator without a clickable.json file

Changes in v6.16.0
------------------

- Enhanced and fixed issues with the qtcreator support
- Fixed the docker_image setting

Changes in v6.15.0
------------------

- Vastly improved qtcreator support using ``clickable ide qtcreator``
- Improved docs
- Updated docs with the new Atom editor plugin
- Fixed the warning about spaces in the path
- Fixed various issues with container mode
- Fixed using gdb and desktop mode

Changes in v6.14.2
------------------

- Fixed issue where some directories were being created by root in the docker container
- Various documentation updates
- Restored the warning about spaces in the source path
- Fixed container mode so it doesn't check for docker images
- Fixed issues with env vars for libraries in container mode
- Added env vars to the ide command

Changes in v6.14.1
------------------

- Fixed issue when using the Atom editor extension
- Merged the C++ templates into one and included qrc compiling
- Minor bug fixes

Changes in v6.14.0
------------------

- Added new setup command to help during initial setup of Clickable
- Prevent building in home directory that isn't a click app

Changes in v6.13.1
------------------

- Fixed issue with an error showing the wrong message
- Fixed multiple ppas in ``dependencies_ppa``

Changes in v6.13.0
------------------

- Fixed packaging issues and published to pypi
- Fixed the builder auto detect showing up when it wasn't needed
- Added better errors when the current user is not part of the docker group
- Remove apps before installing them to avoid apparmor issues
- Various bug fixes
- Added optional git tag versioning in cmake based templates

Changes in v6.12.2
------------------

- Fixed bug checking docker image version
- Renamed build template to builder
- Fixed the publish command

Changes in v6.12.1
------------------

- Bug fixes
- Display nicer error messages when a template fails to be created
- Fixed auto detecting the build template

Changes in v6.12.0
------------------

- Added new feature for debugging via :ref:`valgrind <debugging-with-gdb>`
- Added new :ref:`ide <commands-ide>` command to allow running arbitrary graphical apps like qtcreator
- Code improvements
- Added versioning to the docker images to allow Clickable to depend on certain features in the image

Changes in v6.11.2
------------------

- Fixed the ``review`` and ``clean-build`` commands not working

Changes in v6.11.1
------------------

- Fixed the ``run`` command not working

Changes in v6.11.0
------------------

- Added :ref:`on device debugging with gdb <on-device-debugging>`.
- Deprecated chaining commands (this will be removed in the next major release)
- Fixed the build home directory for libraries
- Added error when trying to use docker images on unsupported host architectures
- Use the host architecture as the default when building in container mode
- Enable localhost access and pseudo-tty in run command
- When using CMake a Release build will be created unless ``--debug`` is specified
- Added new library placeholders
- Added new ``clean-build`` command
- Fixed issues with ``clickable create`` on older versions of Ubuntu
- Various minor bug fixes and code improvements

Changes in v6.10.1
------------------

- Fixed issues installing dependencies when in container mode

Changes in v6.10.0
------------------

- Fix containers being rebuilt when switching between desktop mode and building for amd64
- Enabled compiling rust apps into arm64
- Make ``install_data`` paths relative to the install dir
- Fixed the ``clickable create`` command when using an older version of git

Changes in v6.9.1
-----------------

- Fixed broken lib builds

Changes in v6.9.0
-----------------

- Placeholders are now allowed in env vars
- Changed placeholder syntax to ``${PLACEHOLDER}``, the old syntax is now deprecated
- Replaced ``dependencies_host`` with ``dependencies_build`` to avoid confusion about the name, ``dependencies_build`` is now deprecated
- Normalized env var names
- Added new ``precompiled`` build template to replace the now deprecated ``python`` build template
- Fixed issues using the ``install_*`` configuration options
- ``install_qml`` will now install qml modules to the correct nested path
- A per project home directory gets mounted during the build process
- Cleaned up arch handling and improved conflict detection

Changes in v6.8.2
-----------------

- Fixed broken architecture agnostic builds

Changes in v6.8.1
-----------------

- Fixed new architecture errors breaking architecture agnostic builds

Changes in v6.8.0
-----------------

- Fixed the ``ARCH`` placeholder breaking ``ARCH_TRIPLET`` placeholder
- Added new ``env_vars`` configuration for passing custom env vars to the build process
- Fixed errors on systems where /etc/timezone does not exist
- Added errors to detect conflicting architecture settings
- Improved multi arch support

Changes in v6.7.2
-----------------

- Fixed architecture mismatch error for architecture agnostic templates

Changes in v6.7.0
-----------------

- New error when there is no space left on the disk
- New error when the manifest's architecture does not match the build architecture
- New option to use ``@CLICK_ARCH@`` as the architecture in the manifest to allow Clickable to automatically set the architecture

Changes in v6.6.0
-----------------

- Fixed issue in with timezone detection
- Added better detection for nvidia mode and added a new --no-nvidia argument

Changes in v6.5.0
-----------------

- New bash completion, more info `here <https://gitlab.com/clickable/clickable/blob/master/BASH_COMPLETION.md>`__
- Fixed crash when running in container mode
- Added ``image_setup`` configuration to run arbitrary commands to setup the docker image
- Added arm64 support for qmake builds

Changes in v6.4.0
-----------------

- Use the system timezone when in desktop mode

Changes in v6.3.2
-----------------

- Fixed issues logging process errors
- Fixed issues parsing desktop files

Changes in v6.3.1
-----------------

- Updated `clickable create` to use a new template for a better experience
- Fixed desktop mode issue when the command already exits in the PATH
- Added a prompt for autodetecting the template type
- Improved Clickable's logging

Changes in v6.2.1
-----------------

- Fixed env vars in libs

Changes in v6.2.0
-----------------

- Replaced the ``--debug`` argument with ``--verbose``
- Switched the ``--debug-build`` argument to ``--debug``
- Initial support for running Clickable on MacOS
- Added new desktop mode argument ``--skip-build`` to run an app in desktop mode without recompiling

Changes in v6.1.0
-----------------

- Apps now use host locale in desktop mode
- Added ``--lang`` argument to override the language when running in desktop mode
- Added support for multimedia in desktop mode
- Make app data, config and cache persistent in desktop mode by mounting phablet home folder to ~/.clickable/home
- Added arm64 support and docker images (does not yet work for apps built with qmake)
- :ref:`Added placeholders and env vars to commands and scripts run via clickable <clickable-json-placeholders>`
- :ref:`Added option to install libs/qml/binaries from the docker image into the click package <clickable-json-install_lib>`
- Switched to a clickable specific Cargo home for Rust apps
- Click packages are now deleted from the device after installing
- Fixed ``dependencies_build`` not being allowed as a string
- Fixed issues finding the manifest file

Changes in v6.0.3
-----------------

- Fixed building go apps
- Fixed post build happening after the click is built

Changes in v6.0.2
-----------------

- Fixed container mode

Changes in v6.0.1
-----------------

- Added back click-build with a warning to not break existing apps

Changes in v6.0.0
-----------------

New features
^^^^^^^^^^^^

- When publishing an app for the first time a link to create it on the OpenStore will be shown
- Desktop mode can now use the dark theme with the ``--dark-mode`` argument
- Automatically detect when nvidia drivers are used for desktop mode
- Use native docker nvidia integration rather than nvidia-docker (when the installed docker version supports it)
- The UBUNTU_APP_LAUNCH_ARCH env var is now set for desktop mode
- Added remote gdb debugging in desktop mode via the ``--gdbserver <port>`` argument
- Added configurable ``install_dir``
- Libraries get installed when using ``cmake`` or ``qmake`` build template (into ``install_dir``)

Breaking Changes
^^^^^^^^^^^^^^^^

- The ``click-build`` command has been merged into the ``build`` command
- Removed deprecated configuration properties: ``dependencies``, ``specificDependencies``, and ``dir``
- Removed deprecated library configuration format
- Removed deprecated lxd support
- Moved the default build directory from ``build`` to ``build/<arch triplet>/app``
- Moved the default library build directory to ``build/<arch triplet>/<lib name>``
- Removed deprecated vivid support

Bug Fixes
^^^^^^^^^

- Fixed utf-8 codec error
- Use separate cached containers when building libraries
- Automatically rebuild the cached docker image for dependencies

Changes in v5.14.1
------------------

- Limit make processes to the number of cpus on the system
- Fix missing directory for newer Rust versions
- Fix placeholders not being absolute

Changes in v5.14.0
------------------

- Added check for outdated containers when using custom dependencies
- Fixed building libraries

Changes in v5.13.3
------------------

- Fixed the update command so it updates all available Docker images

Changes in v5.13.2
------------------

- Fixed libraries not building after latest update

Changes in v5.13.1
------------------

- Follow up fixes for dependencies not being used for the first run

Changes in v5.13.0
------------------

- Added new :ref:`debugging with gdb <debugging-with-gdb>` argument
- Added new :ref:`test <commands-test>` command for running tests inside the container
- When running in desktop mode, cache/share/config directories are automatically created
- Fixed hidden build directories causing errors when looking for the manifest
- Fixed issue with cordova building
- Fixed dependencies not being used the first time clickable is run

Changes in v5.12.3
------------------

- Fixed slowdown when running clickable in a non-project directory

Changes in v5.12.2
------------------

- Fixed ``scripts`` breaking Clickable

Changes in v5.12.1
------------------

- Fixed issues with build dir

Changes in v5.12.0
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
