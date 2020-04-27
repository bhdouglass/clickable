.. _builders:

Builders
========
Builders have been called Build Templates in the early days of Clickable.

pure-qml-qmake
--------------

A purely qml qmake project.

qmake
-----

A project that builds using qmake (has more than just QML).

pure-qml-cmake
--------------

A purely qml cmake project

cmake
-----

A project that builds using cmake (has more than just QML)

custom
------

A custom build command will be used.

cordova
-------

A project that builds using cordova

pure
----

A project that does not need to be compiled. All files in the project root will be copied into the click.

precompiled
-----------

A project that does not need to be compiled. All files in the project root will
be copied into the click. There may be precompiled binaries or libraries
included in apps build with this builder. Specifying the
:ref:`restrict_arch <clickable-json-restrict_arch>` in the clickable.json file
can be useful with this builder.

python
------

Deprecated, use "precompiled" instead.

go
--

A project that uses go version 1.6.

rust
----

A project that uses rust. Debug builds can be enabled by specifying ``--debug``.
