Chroot basics
#############

:keywords: linux, chroot, hacking
:tags: linux, chroot, hacking
:date: 2018-12-29
:Status: draft
:lang: en
:slug: chroot-basics

In this post I am going to write about *chroot*.
We will see, how to create step by step, how to run application in *chroot* and how to configure *ssh* to jail users in *chroot*.

What is *chroot*?
-----------------

*Chroot* is shortcut for *change root* and as its name would suggest, it changes root directory for process.
In effect, the process and all its children whenever they access path `/`, in fact they will access changed root.

Current root directory can be retrieved by *proc* subsystem.
Ex. let's take *bash* process with *pid* 8429 which has been executed in *chroot*.
In main system, its root directory is set to:

.. code-block:: console

   # ls -l /proc/8429/root
   lrwxrwxrwx. 1 root root 0 01-05 11:04 /proc/8429/root -> /tmp/ch

But, when we read the same attribute in *chroot*, we will get

.. code-block:: console

    # ls -l /proc/8429/root
    lrwxrwxrwx. 1 0 0 0 Jan  5 10:04 /proc/8429/root -> /

As we can see, the process which has been run in *chroot* isn't aware that its root has been changed.

How to make your first *chroot*?
--------------------------------

I will show you step by step how to make your first *chroot*.
I will also show you every error, because I think that these errors help you understand how *chroot* is working and why we copy these files and not the others.

Our first goal is run `bash` in *chroot*.
First, we need to create directory for *chroot*, next we need to copy `bash` binary to it (we use `/bin` for binaries)

.. code-block:: console

   $ mkdir /tmp/first_chroot
   $ mkdir /tmp/first_chroot/bin
   $ cp /bin/bash /tmp/first_chroot/bin/
