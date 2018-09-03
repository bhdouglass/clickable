.. _continuous-integration:

Continuous Integration
======================

Clickable CI Docker Images
--------------------------

Two docker images are available for easily using Clickable with a continuous
integration setup. They can be found on Docker hub: ``clickable/ci-15.04-armhf``
and ``clickable/ci-16.04-armhf`` for vivid/15.04 and xenial/16.04 respectively.
The images come with Clickable pre installed and already setup in
container mode.

GitLab Example
--------------

With GitLab's CI solution it is trivial to add Clickable building and publish
to your click apps. For an example of this in action, check out the
`Clickable GitLab example app <https://gitlab.com/clickable/clickable-gitlab-ci-test>`__.

To implement this in your own repository, create a ``.gitlab-ci.yml``:

.. code-block:: yaml

    build_vivid:
      image: clickable/ci-15.04-armhf
      script:
      - clickable --vivid clean build click-build review publish

    build_xenial:
      image: clickable/ci-16.04-armhf
      script:
      - clickable clean build click-build review publish

After that's setup, the last step is to add the environment variable
``OPENSTORE_API_KEY`` to your GitLab project (You can find your OpenStore
api key when you log into the OpenStore).
