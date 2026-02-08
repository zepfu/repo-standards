Docker Standards
================

Standards for Docker containers and builds.

**Coming soon!**

For now, use the reusable workflow:

.. code-block:: yaml

   jobs:
     docker-build:
       uses: zepfu/repo-standards/.github/workflows/reusable-docker-build.yml@main
       with:
         platforms: 'linux/amd64'
