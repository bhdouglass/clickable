.. _build-templates:

Build Templates
===============

+----------------+
| pure-qml-qmake |
+----------------+

A purely qml qmake project.

+-------+
| qmake |
+-------+

A project that builds using qmake (has more than just QML).

+----------------+
| pure-qml-cmake |
+----------------+

A purely qml cmake project

+-------+
| cmake |
+-------+

A project that builds using cmake (has more than just QML)

+--------+
| custom |
+--------+

A custom build command will be used.

+---------+
| cordova |
+---------+

A project that builds using cordova

+------+
| pure |
+------+

A project that does not need to be compiled. All files in the project root will be copied into the click.

+--------+
| python |
+--------+

A project that uses python and does not need to be compiled.

+----+
| go |
+----+

A project that uses go.
This uses golang 1.6 and every optimized fork for go 1.6 from `gopkg.in/qml.v1` for example `github.com/nanu-c/qml-go`
