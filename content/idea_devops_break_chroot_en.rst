Hacking the chroot/docker
#########################

:keywords: linux, chroot, hacking, docker
:tags: linux, chroot, hacking, docker
:date: 2019-01-19
:Status: draft
:slug: chroot-breaking-1
:lang: en

In this post I'm going to access supervisor's filesystem when having *root* in *chroot*.
With that, I want to show you, why you should never give root access to users in *chroot*.

Crash course
------------

Because *docker* (like most of container technologies) uses *chroot*, exiting a *chroot* or *docker* will use the same technique.
Presented method need root access in docker run as *privileged* (in case you use docker).

.. code-block:: console

    # docker run -it --privileged centos /bin/bash
    # mknod /tmp/host_disk b 259 1
    # mount /tmp/host_disk /mnt/
    # chroot /mnt/ /bin/bash

Method description
------------------

This method uses *chroot* to the supervisor's *filesystem*.
Usually, we don't have ``/dev/`` directory in *chroot*, so we cannot 
