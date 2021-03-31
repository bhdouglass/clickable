.. _clickable-json:

clickable.json Format
=====================

Example:

.. code-block:: javascript

    {
        "builder": "cmake",
        "scripts": {
            "fetch": "git submodule update --init"
        },
        "dependencies_target": [
            "libpoppler-qt5-dev"
        ]
    }

.. _clickable-json-placeholders:

Placeholders & Environment Variables
------------------------------------

Placeholders are values provided by Clickable that can be used in some
configuration fields as ``${PLACEHOLDER}`` (``$PLACEHOLDER`` is deprecated syntax).
All placeholders are provided as environment variables during build, additionally.
For custom environment variables see :ref:`env_vars <clickable-json-env_vars>`.

The following table lists all available placeholders.

======================= ======
Placeholder             Output
======================= ======
ARCH                    Target architecture (``armhf``, ``arm64``, ``amd64`` or ``all``)
ARCH_TRIPLET            Target architecture triplet (``arm-linux-gnueabihf``, ``aarch63-linux-gnu``, ``x86_64-linux-gnu`` or ``all``)
NUM_PROCS               Number of build jobs recommended (``make_jobs``) and used by the CMake and QMake builders
ROOT                    Value of ``root_dir``
BUILD_DIR               Value of ``build_dir``
SRC_DIR                 Value of ``src_dir``
INSTALL_DIR             Value of ``install_dir``
CLICK_LD_LIBRARY_PATH   ``${INSTALL_DIR}/lib/${ARCH_TRIPLET}`` (will be in ``LD_LIBRARY_PATH`` at runtime) or ``${INSTALL_DIR}/lib`` for architecture independent apps
CLICK_QML2_IMPORT_PATH  ``${INSTALL_DIR}/lib/${ARCH_TRIPLET}`` (will be in ``QML2_IMPORT_PATH`` at runtime) or ``${INSTALL_DIR}/qml`` for architecture independent apps
CLICK_PATH              ``${INSTALL_DIR}/lib/${ARCH_TRIPLET}/bin`` or ``${INSTALL_DIR}`` for architecture independent apps (will be in ``PATH`` at runtime)
<lib>_LIB_BUILD_DIR     Value of ``build_dir`` from library with name ``<lib>`` (see :ref:`libraries <clickable-json-libraries>`), where the library name consists solely of capital letters (e.g. from lib name ``my-libC++`` this env var would be ``MY_LIBC___LIB_BUILD_DIR``)
<lib>_LIB_INSTALL_DIR   Value of ``install_dir`` from library with name ``<lib>`` (e.g. ``OPENCV_LIB_INSTALL_DIR``)
<lib>_LIB_SRC_DIR       Value of ``src_dir`` from library with name ``<lib>`` (e.g. ``OPENCV_LIB_SRC_DIR``)
======================= ======

Parameters accepting placeholders:
``root_dir``, ``build_dir``, ``src_dir``, ``install_dir``,
``app_lib_dir``, ``app_bin_dir``, ``app_qml_dir``,
``gopath``, ``cargo_home``, ``scripts``, ``build``,
``build_args``, ``make_args``, ``postmake``, ``postbuild``,
``prebuild``,
``install_lib``, ``install_qml``, ``install_bin``,
``install_data`` and ``env_vars``.

This is an ordered list. Parameters that are used as placeholders themselves accept only predecessors.
Ex: ``${ROOT}`` can be used in ``src_dir``, but not vice-versa.

Example:

.. code-block:: javascript

    {
        "builder": "cmake",
        "build_dir": "${ROOT}/build/${ARCH_TRIPLET}/myApp"
    }

clickable_minimum_required
--------------------------

Optional, a minimum Clickable version number required to build the project.
Ex: ``"6"`` or ``"5.4.0"``

.. _clickable-json-qt_version:

qt_version
----------

Qt version consisting of major and minor version. This value is used to
determine the framework automatically. Defaults to ``5.12``.
Ex: ``5.9``

.. _clickable-json-framework:

framework
---------

The SDK framework which the app should be built for. This allows Clickable to
choose the correct docker image and set the ``framework`` field in the manifest
accordingly, if desired.
Ex: ``ubuntu-sdk-16.04.4``

.. _clickable-json-restrict_arch:

restrict_arch
-------------

Optional, specifies an exclusive architecture that this configuration is compatible with.
This prevents the app from being build for other architectures and may also prevent the desktop mode.

To specify the architecture for building use the cli argument instead (ex: ``--arch arm64``).

arch
----

Deprecated, use ``restricted_arch`` instead.

.. _clickable-json-builder:

builder
-------

Optional, see :ref:`builders <builders>` for the full list of options.

template
--------

Deprecated, use :ref:`builder <clickable-json-builder>` instead.

prebuild
--------

Optional, a custom command to run from the root dir, before a build.

build
-----

A custom command to run from the build dir. Required if using the ``custom``
builder, ignored otherwise.

postmake
---------

Optional, a custom command to execute from the build directory, after make (during build).

postbuild
---------

Optional, a custom command to execute from the build dir, after build and before click packaging.

.. _clickable-json-env_vars:

env_vars
--------

Optional, environment variables to be set in the build container. Ex:

.. code-block:: javascript

    "env_vars": {
        "TARGET_SYSTEM": "UbuntuTouch"
    }

When passing ``--debug`` to Clickable, ``DEBUG_BUILD=1`` is set as an environment variable, additionally.

build_args
----------

Optional, arguments to pass to qmake or cmake. When using ``--debug``,
``CONFIG+=debug`` is additionally appended for qmake and
``-DCMAKE_BUILD_TYPE=Debug`` for cmake and cordova builds. Ex: ``CONFIG+=ubuntu``

Can be specified as a string or a list of strings.

.. _clickable-json-make-args:

make_args
---------

Optional, arguments to pass to make, e.g. a target name. To avoid configuration
conflicts, the number of make jobs should not be specified here, but using
``make_jobs`` instead, so it can be overriden by the according environment variable.

Can be specified as a string or a list of strings.

.. _clickable-json-make-jobs:

make_jobs
---------

Optional, the number of jobs to use when running make, equivalent to make's ``-j``
option. If left blank this defaults to the number of CPU cores.

launch
------

Optional, a custom command to launch the app, used by ``clickable launch``.

.. _clickable-json-build_dir:

build_dir
---------

Optional, a custom build directory. Defaults to ``${ROOT}/build/${ARCH_TRIPLET}/app``.
Thanks to the architecture triplet, builds for different architectures can
exist in parallel.

src_dir
-------

Optional, a custom source directory. Defaults to ``${ROOT}``

install_dir
-----------

Optional, a custom install directory (used to gather data that goes into the click package).
Defaults to ``${BUILD_DIR}/install``

.. _clickable-json-install_lib:

install_lib
-----------

Optional, additional libraries that should be installed with the app and be in ``LD_LIBRARY_PATH`` at runtime.
The destination directory is ``${CLICK_LD_LIBRARY_PATH}``. Ex:

.. code-block:: javascript

    "install_lib": [
        "/usr/lib/${ARCH_TRIPLET}/libasound.so*"
    ]

Can be specified as a string or a list of strings. Paths must not contain ``"`` characters.
Supports wildcards as this actually calls ``ls "<path>"`` in a bash.

install_qml
-----------

Optional, additional QML files or directories that should be installed with the app and be in
``QML2_IMPORT_PATH`` at runtime. The destination directory is ``${CLICK_QML2_IMPORT_PATH}``. Ex:

.. code-block:: javascript

    "install_qml": [
        "/usr/lib/${ARCH_TRIPLET}/qt5/qml/Qt/labs/calendar"
    ]

QML modules will be installed to the correct directory based on the name of the module.
In the above example it will be installed to ``lib/${ARCH_TRIPLET}/Qt/labs/calendar``
because the module specified in the qmldir file is ``Qt.labs.calendar``.
Can be specified as a string or a list of strings. Paths must not contain ``"`` characters.
Supports wildcards as this actually calls ``ls "<path>"`` in a bash.

install_bin
-----------

Optional, additional executables that should be installed with the app and be in ``PATH`` at runtime.
The destination directory is ``${CLICK_PATH}``. Ex:

.. code-block:: javascript

    "install_bin": [
        "/usr/bin/htop"
    ]

Can be specified as a string or a list of strings. Paths must not contain ``"`` characters.
Supports wildcards as this actually calls ``ls "<path>"`` in a bash.

install_data
------------

Optional, additional files or directories that should be installed with the app.
Needs to be specified as a dictionary with absolute source paths as keys and destinations as value. Ex:

.. code-block:: javascript

    "install_data": {
        "${ROOT}/packaging/manifest.json": "${INSTALL_DIR}",
        "${ROOT}/packaging/myapp.desktop": "${INSTALL_DIR}"
    },

Can be specified as a string or a list of strings. Paths must not contain ``"`` characters.
Supports wildcards as this actually calls ``ls "<src>"`` in a bash. ``${INSTALL_DIR}`` is
added as prefix if path is not relative to the install dir.

kill
----

Optional, a custom process name to kill (used by ``clickable launch`` to kill the app before
relaunching it). If left blank the process name will be assumed.

scripts
-------

Optional, an object detailing custom commands to run. For example:

.. code-block:: javascript

    "scripts": {
        "fetch": "git submodule update --init",
        "echo": "echo ${ARCH_TRIPLET}"
    }

That enables the use of ``clickable fetch`` and ``clickable echo``.

.. _clickable-json-default:

default
-------

Optional, sub-commands to run when no sub-commands are
specified (running simply ``clickable``). Defaults to ``clean build install launch``.
The ``--dirty`` cli argument removes ``clean`` from that list.

Can be specified as a string or a list of strings.

.. _clickable-json-dirty:

dirty
-----

Optional, whether or not do a dirty build, avoiding to clean the build directory
before building. You may also specify this as a cli arg (``--dirty``).
The default is ``false``.

.. _clickable-json-dependencies_host:

dependencies_host
-----------------

Optional, a list of dependencies that will be installed in the build container.

Add tools here that are part of your build tool chain.

Can be specified as a string or a list of strings.

dependencies_build
------------------

Deprecated, use :ref:`dependencies_host <clickable-json-dependencies_host>` instead.

.. _clickable-json-dependencies_target:

dependencies_target
-------------------

Optional, a list of dependencies that will be installed in the build container.
These will be assumed to be ``dependency:arch`` (where ``arch`` is the target
architecture), unless an architecture specifier
is already appended.

Add dependencies here that your app depends on.

Can be specified as a string or a list of strings.

.. _clickable-json-dependencies-ppa:

dependencies_ppa
----------------

Optional, a list of PPAs, that will be enabled in the build container. Ex:

.. code-block:: javascript

    "dependencies_ppa": [
        "ppa:bhdouglass/clickable"
    ]

Can be specified as a string or a list of strings.

.. _clickable-json-docker-image:

image_setup
-----------
Optional, dictionary containing setup configuration for the docker image used.
The image is based on the default image provided by Clickable. Example:

.. code-block:: javascript

    "image_setup": {
        "env": {
            "PATH": "/opt/someprogram/bin:$PATH"
        },
        "run": [
            "rustup default nightly",
            "rustup install 1.39.0"
        ]
    }

run
^^^
Optional, a list of commands to run on image setup (each added as `RUN <cmd>` to
the corresponding Dockerfile).

These commands also run in container mode (CI).

env
^^^
Optional, a dictionary of env vars to add during image setup (each added as
`ENV <key>="<val>"` to the corresponding Dockerfile).

These are ignored in container mode (use
:ref:`env_vars <clickable-json-env_vars>` instead).

docker_image
------------

Optional, the name of a docker image to use. When building a custom docker image
it's recommended to use one of the Clickable images as a base. You can find them
on `Docker Hub <https://hub.docker.com/u/clickable>`__.

ignore
------

Optional, a list of files to ignore when building with ``pure`` builder
Example:

.. code-block:: javascript

    "ignore": [
        ".clickable",
        ".git",
        ".gitignore",
        ".gitmodules"
    ]

Can be specified as a string or a list of strings.

.. _clickable-json-gopath:

gopath
------

Optional, the gopath on the host machine. If left blank, the ``GOPATH`` env var will be used.

.. _clickable-json-cargo_home:

cargo_home
----------

Optional, the Cargo home path on the host machine that is used for caching
(namely its subdirs ``registry``, ``git`` and ``.package-cache``).
Defaults to ``~/.clickable/cargo``.

.. _clickable-json-build-args:

root_dir
--------

Optional, specify a different root directory for the project. For example,
if you clickable.json file is in ``platforms/ubuntu_touch`` and you want to include
code from root of your project you can set ``root_dir: "../.."``. Alternatively you can run
clickable from the project root in that case via
``clickable -c platforms/ubuntu_touch/clickable.json``.

.. _clickable-json-test:

test
----

Optional, specify a test command to be executed when running ``clickable test``.
The default is ``qmltestrunner``.

.. _clickable-json-libraries:

libraries
---------
Optional, dependencies to be build by running ``clickable build-libs``.
It's a dictionary of dictionaries similar to the clickable.json itself. Example:

.. code-block:: javascript

    "libraries": {
        "opencv": {
            "builder": "cmake",
            "make_jobs": "1",
            "build_args": [
                "-DCMAKE_BUILD_TYPE=Release",
                "-DBUILD_LIST=core,imgproc,highgui,imgcodecs",
                "-DBUILD_SHARED_LIBS=OFF"
            ]
            "prebuild": "git submodule update --init --recursive"
        }
    }

The keywords ``test``, ``install_dir``, ``prebuild``, ``build``, ``postbuild``,
``postmake``, ``make_jobs``, ``make_args``, ``env_vars``, ``build_args``, ``docker_image``,
``dependencies_host``, ``dependencies_target`` and ``dependencies_ppa``,
can be used for a library the same way as described above for the app.

In addition to the :ref:`placeholders <clickable-json-placeholders>` described above,
the following placeholders are available:

============= ======
Placeholder   Output
============= ======
NAME          The library name (key name in the ``libraries`` dictionary)
============= ======

A single library can be build by specifying its name as
``clickable build-libs lib1 --arch arm64`` to build the library with name
``lib1`` for the architecture ``arm64``.
``clickable clean-libs lib1 --arch arm64`` cleans the libraries build dir.
``clickable test-libs lib1`` tests the library.

builder
^^^^^^^
Required, but only ``cmake``, ``qmake`` and ``custom`` are allowed.

src_dir
^^^^^^^
Optional, library source directory. Must be relative to the project root. Defaults to ``${ROOT}/libs/${NAME}``

build_dir
^^^^^^^^^
Optional, library build directory. Must be relative to the project root. Defaults to ``${ROOT}/build/${ARCH_TRIPLET}/${NAME}``.
Thanks to the architecture triplet, builds for different architectures can
exist in parallel.

Removed keywords
----------------
The following keywords are no longer supported:

- ``dependencies`` (use ``dependencies_target`` and ``dependencies_host`` instead)
- ``specificDependencies``
- ``dir`` (use ``build_dir`` instead)
- ``lxd``
- ``premake`` (use ``prebuild``, ``postmake`` or ``postbuild`` instead)
- ``ssh`` (use program option ``--ssh`` or environment variable ``CLICKABLE_SSH`` instead)
- ``chroot``
- ``sdk``
- ``package``
- ``app``
