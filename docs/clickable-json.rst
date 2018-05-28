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
        "dependencies": [
            "libpoppler-qt5-dev"
        ]
    }


package
-------

The full package name (appname.developer). This is optional and will be read
from manifest.json if left blank.

app
---

The app name (appname.developer). This is optional and will be read
from manifest.json if left blank.

sdk
---

Optional, Defaults to `ubuntu-sdk-15.04`

arch
----

Optional, the default is armhf. You may also specify this as a cli arg
(ex: ``--arch="armhf"``)

prebuild
--------

Optional, a custom command to run before a build.

template
--------

Optional, see :ref:`build template <build-templates>` for the full list of options.
If left blank the template will be auto detected.

premake
-------

Optional, a custom command to execute before make is run.

build
-----

Optional, a custom command to run instead of the default build. If using
the `custom` template this is required.

postbuild
---------

Optional, a custom command to execute after build and before click build.

launch
------

Optional, a custom command to launch the app.

ssh
---

Optional, the IP of the device you wish to install and launch the app on.

dir
---

Optional, a custom build directory. Defaults to ``./build/``

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

To run the command on the device use the ``--device`` argument ( ex: ``clickable test --device`` ).

chroot
------

Optional, whether or not to use a chroot to build the app. Default is to use
docker to build the app. Chroots are deprecated and their support will be removed
in a future version of clickable.

lxd
---

Optional, whether or not to use a lxd container to build the app. Default is to use
docker to build the app. LXD is deprecated and its support will be removed
in a future version of clickable.

default
-------

Optional, a list of space separated sub-commands to run when no sub-commands are
specified. Defaults to ``kill clean build click-build install launch``.

dependencies
------------

Optional, a list of dependencies that will be installed in the build container.
These will be assumed to be `dependencie:arch` unless `specificDependencies`
is set to `true`.

ignore
------

Optional, a list of files to ignore when building a `pure` template
Example:

.. code-block:: javascript

    "ignore": [
        ".clickable",
        ".git",
        ".gitignore",
        ".gitmodules"
    ]


make_jobs
---------

Optional, the number of jobs to use when running make, equivalent to make's `-j`
option. If left blank this defaults to the number of cpus your computer has.

gopath
------

Optional, the gopath on the host machine. If left blank, the ``GOPATH`` env var will be used.
