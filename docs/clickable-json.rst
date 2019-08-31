.. _clickable-json:

clickable.json Format
=====================

Example:

.. code-block:: javascript

    {
        "template": "cmake",
        "scripts": {
            "test": "make test"
        },
        "dependencies_target": [
            "libpoppler-qt5-dev"
        ]
    }

.. _clickable-json-placeholders:

Placeholders
------------

============= ======
Placeholder   Output
============= ======
$ARCH_TRIPLET Target architecture triplet (``arm-linux-gnueabihf``, ``x86_64-linux-gnu`` or ``all``)
$ROOT         Value of ``root_dir``
$BUILD_DIR    Value of ``build_dir``
$SRC_DIR      Value of ``src_dir``
$INSTALL_DIR  Value of ``install_dir``
============= ======

Parameters accepting placeholders: ``root_dir``, ``build_dir``, ``src_dir``, ``install_dir``, ``gopath``, ``cargo_home``, ``scripts``, ``build``, ``build_args``, ``make_args``, ``postmake``, ``postbuild``, ``prebuild``. This is an ordered list. Parameters that are used as placeholders themselfs accept only predecessors. Ex: ``$ROOT`` can be used in ``src_dir``, but not vice-versa.

Example:

.. code-block:: javascript

    {
        "template": "cmake",
        "build_dir": "$ROOT/build/$ARCH_TRIPLET"
    }

clickable_minimum_required
--------------------------

Optional, a minimum Clickable version number required to build the project.
Ex: ``"4"`` or ``"5.4.0"``

.. _clickable-json-arch:

arch
----

Optional, the default is armhf. You may also specify this as a cli arg
(ex: ``--arch="armhf"``)

.. _clickable-json-template:

template
--------

Optional, see :ref:`build template <build-templates>` for the full list of options.
If left blank the template will be auto detected.


prebuild
--------

Optional, a custom command to run before a build.

build
-----

Optional, a custom command to run instead of the default build. If using
the ``custom`` template this is required.

postbuild
---------

Optional, a custom command to execute after build and before click build.


postmake
---------

Optional, a custom command to execute after make (during build).

launch
------

Optional, a custom command to launch the app.

.. _clickable-json-build_dir:

build_dir
---------

Optional, a custom build directory. Defaults to ``$ROOT/build/``

dir
---

Deprecated, use ``build_dir`` instead.

src_dir
-------

Optional, a custom source directory. Defaults to ``$ROOT``

install_dir
-----------

Optional, a custom install directory (used to gather data that goes into the click package). Defaults to ``$BUILD_DIR/tmp``

kill
----

Optional, a custom process name to kill (useful for killing the running app,
then relaunching it). If left blank the process name will be assumed.

scripts
-------

Optional, an object detailing custom commands to run. For example:

.. code-block:: javascript

    {
        "test": "make test",
        "echo": "echo Hello World"
    }

.. _clickable-json-lxd:

lxd
---

Optional, whether or not to use a lxd container to build the app. Default is to use
docker to build the app. LXD is deprecated and its support will be removed
in a future version of clickable.

.. _clickable-json-default:

default
-------

Optional, a list of space separated sub-commands to run when no sub-commands are
specified. Defaults to ``clean build click-build install launch``.

Can be specified as a string or a list of strings.

.. _clickable-json-dependencies_build:

dependencies_build
------------------

Optional, a list of dependencies that will be installed in the build container.

These will not be installed in the target arch.

Can be specified as a string or a list of strings.

.. _clickable-json-dependencies_target:

dependencies_target
-------------------

Optional, a list of dependencies that will be installed in the build container.
These will be assumed to be ``dependency:arch``, unless an architecture specifier
is already appended. In desktop mode ``dependencies_target`` is handled just
like ``dependencies_build``.

Add dependencies here that your app depends on.

Can be specified as a string or a list of strings.

dependencies
------------

This parameter is deprecated and will be removed in a future version.
Use ``dependencies_build`` (where ``specificDependencies`` is ``true``)
or ``dependencies_target`` instead!

Optional, a list of dependencies that will be installed in the build container.
These will be assumed to be ``dependency:arch`` unless ``specificDependencies``
is set to ``true``.

Can be specified as a string or a list of strings.

.. _clickable-json-dependencies-ppa:

dependencies_ppa
----------------

Optional, a list of PPAs, that will be enabled in the build container. This is
only supported for docker mode. Ex:

.. code-block:: javascript

    "dependencies_ppa": [
        "ppa:bhdouglass/clickable"
    ]

Can be specified as a string or a list of strings.

.. _clickable-json-docker-image:

docker_image
------------

Optional, the name of a docker image to use. When building a custom docker image
it's recommended to use one of the Clickable images as a base. You can find them
on `Docker Hub <https://hub.docker.com/r/clickable/ubuntu-sdk/tags/>`__.

ignore
------

Optional, a list of files to ignore when building a ``pure`` template
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

Optional, the Cargo home path (usually ``~/.cargo``) on the host machine.
If left blank, the ``CARGO_HOME`` env var will be used.

.. _clickable-json-build-args:

build_args
----------

Optional, arguments to pass to qmake or cmake. When using ``--debug-build``,
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
option. If left blank this defaults to ``-j``, allowing make to execute many
recipes simultaneously.

.. _clickable-json-dirty:

dirty
-----

Optional, whether or not do a dirty build, avoiding to clean the build directory
before building. You may also specify this as a cli arg (``--dirty``).
The default is ``false``.

.. _clickable-json-libraries:

root_dir
--------

Optional, specify a different root directory for the project. For example,
if you clickable.json file is in ``platforms/ubuntu_touch`` and you want to include
code from root of your project you can set ``root_dir: "../.."``.

.. _clickable-json-test:

test
----

Optional, specify a different test command to run when running ``clickable test``.
The default is ``qmltestrunner``.

libraries
---------
Optional, libraries to be build in the docker container by calling ``clickable build-libs``.
It's a dictionary of dictionaries basically looking like the clickable.json itself. Example:

.. code-block:: javascript

    "libraries": {
        "opencv": {
            "template": "cmake",
            "make_jobs": "4",
            "build_args": [
                "-DCMAKE_BUILD_TYPE=Release",
                "-DBUILD_LIST=core,imgproc,highgui,imgcodecs",
                "-DBUILD_SHARED_LIBS=OFF"
            ]
            "prebuild": "git submodule update --init --recursive"
        }
    }

The keywords ``prebuild``, ``build``, ``postbuild``,
``postmake``, ``make_jobs``, ``make_args``, ``build_args``, ``docker_image``,
``dependencies_build``, ``dependencies_target`` and ``dependencies_ppa``,
can be used for a library the same way as described above for the app. The
libraries are compiled for the same architecture as specified for the app itself.

Consider defining a custom build directory for the app itself (Ex: ``build/app``). Otherwise cleaning the app cleans the library, too.

In addition to the :ref:`placeholders <clickable-json-placeholders>` described above, the following placeholders are available:

============= ======
Placeholder   Output
============= ======
$NAME         The library name (key name in the ``libraries`` dictionary)
============= ======

A single library can be build by specifying its name as ``clickable build-libs lib1`` to build the library with name ``lib1``.

template
^^^^^^^^
Required, but only ``cmake``, ``qmake`` and ``custom`` are allowed.

src_dir
^^^^^^^
Optional, library source directory. Must be relative to the project root. It defaults to ``$ROOT/libs/$NAME``

build_dir
^^^^^^^^^
Optional, library build directory. Must be relative to the project root. It
defaults to ``$ROOT/build/$NAME/$ARCH_TRIPLET``. Thanks to the architecture triplet, builds for different architectures can
exist in parallel.

install_dir
^^^^^^^^^^^
Optional, a custom install directory. Defaults to ``$BUILD_DIR/install``

dir
^^^
Deprecated, use ``build_dir`` instead.
