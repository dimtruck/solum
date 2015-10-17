==========================
Enabling Solum in DevStack
==========================

1. Install Docker, to be used by our build service::

    http://docs.docker.io/installation/

2. Download DevStack::

    git clone https://git.openstack.org/openstack-dev/devstack.git
    cd devstack

3. Add this repo as an external repository::

    > cat local.conf
    [[local|localrc]]
    enable_plugin solum git://git.openstack.org/openstack/solum

4. Run ``stack.sh``.

Note: This setup will produce virtual machines, not Docker containers.
      For an example of the Docker setup, see::

      http://wiki.openstack.org/Solum/Docker
