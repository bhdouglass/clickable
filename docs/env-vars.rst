.. _env-vars:

Environment Variables
=====================

Environment variables will override values in the clickable.json and can be
overridden by command line arguments.

In contrast to the environment variables described here that configure
Clickable, there are :ref:`environment variables <clickable-json-placeholders>` set by
Clickable to be used during build.

``CLICKABLE_ARCH``
------------------

Restricts build commands (``build``, ``build-libs``, ``desktop``) to the specified architecture. Architecture agnostic builds (``all``) are not affected. Useful in container mode.

``CLICKABLE_QT_VERSION``
------------------------

Overrides the clickable.json's :ref:`qt_version <clickable-json-qt_version>`.

``CLICKABLE_FRAMEWORK``
-----------------------

Overrides the clickable.json's :ref:`builder <clickable-json-framework>`.

``CLICKABLE_BUILDER``
---------------------

Overrides the clickable.json's :ref:`builder <clickable-json-builder>`.

``CLICKABLE_BUILD_DIR``
-----------------------

Overrides the clickable.json's :ref:`dir <clickable-json-build_dir>`.

``CLICKABLE_DEFAULT``
---------------------

Overrides the clickable.json's :ref:`default <clickable-json-default>`.

``CLICKABLE_MAKE_JOBS``
-----------------------

Overrides the clickable.json's :ref:`make_jobs <clickable-json-make-jobs>`.

``GOPATH``
----------

Overrides the clickable.json's :ref:`gopath <clickable-json-gopath>`.

``CARGO_HOME``
--------------

Overrides the clickable.json's :ref:`cargo_home <clickable-json-cargo_home>`.

``CLICKABLE_DOCKER_IMAGE``
--------------------------

Overrides the clickable.json's :ref:`docker_image <clickable-json-docker-image>`.

``CLICKABLE_BUILD_ARGS``
------------------------

Overrides the clickable.json's :ref:`build_args <clickable-json-build-args>`.

``CLICKABLE_MAKE_ARGS``
------------------------

Overrides the clickable.json's :ref:`make_args <clickable-json-make-args>`.

``OPENSTORE_API_KEY``
---------------------

Your api key for :ref:`publishing to the OpenStore <publishing>`.

``CLICKABLE_CONTAINER_MODE``
----------------------------

Same as :ref:`--container-mode <container-mode>`.

``CLICKABLE_SERIAL_NUMBER``
---------------------------

Same as :ref:`--serial-number <multiple-devices>`.

``CLICKABLE_SSH``
-----------------

Same as :ref:`--ssh <ssh>`.

``CLICKABLE_OUTPUT``
--------------------

Override the output directory for the resulting click file

``CLICKABLE_NVIDIA``
--------------------

Same as :ref:`--nvidia <nvidia>`.

``CLICKABLE_NO_NVIDIA``
-----------------------

Same as :ref:`--no-nvidia <nvidia>`.

``CLICKABLE_DIRTY``
-------------------

Overrides the clickable.json's :ref:`dirty <clickable-json-dirty>`.

``CLICKABLE_NON_INTERACTIVE``
-----------------------------

Same as ``--non-interactive``

``CLICKABLE_DEBUG_BUILD``
-------------------------

Same as ``--debug``

``CLICKABLE_TEST``
------------------

Overrides the clickable.json's :ref:`test <clickable-json-test>`.

``CLICKABLE_DARK_MODE``
-----------------------

Same as ``--dark-mode``

``CLICKABLE_ENV_<CUSTOM>``
--------------------------

Adds custom env vars to the build container. E.g. set
``CLICKABLE_ENV_BUILD_TESTS=ON`` to have ``BUILD_TESTS=ON`` set in the build
container.

Overrides env vars in :ref:`test <clickable-json-env_vars>`.
