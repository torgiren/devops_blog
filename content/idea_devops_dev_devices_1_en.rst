Common /dev/ devices
####################

:keywords: linux, dev, kernel
:tags: linux, dev, kernel
:date: 2019-12-15
:Status: draft
:slug: dev-devices
:lang: en

In this post, I will show you a few GNU/Linux devices, which could be useful for SysOps.

.. youtube:: k0_-xWhl6sk

Preface
-------

All of the special device files that are handled by the kernel are described in `<https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/devices.txt/>`_.

I will focus on these I find most often used.

/dev/null
---------

Probably, the most often used device is ``/dev/null``.
This is the empty device and that means, that we don't get any data when we try to read from it.

.. code:: console

  $ hexdump -C /dev/null 

however, writing will lead to drop data

.. code:: console

  $ echo "test" >/dev/null

The most often use case of this device is to write data to it when we don't what to get them on screen:

.. code:: console

  $ ps aux > /dev/null

/dev/zero
---------

``/dev/zero`` device, as the name suggests, always return zero.
Usually one only read from it.
Zeros are mostly used while creating files which should be allocated immediately (in contrast to ``truncate`` command)

.. code:: console

  $ dd if=/dev/zero of=/tmp/file.dat bs=1k count=10k
  10240+0 records in
  10240+0 records out
  10485760 bytes (10 MB, 10 MiB) copied, 0.0252958 s, 415 MB/s

/dev/random and /dev/urandom
----------------------------

``/dev/random`` and ``/dev/urandom`` devices return random data from kernel entropy pool, but they differ in their behavior in case of an emptying pool.
In the case of ``/dev/random``, read operation is being blocked until new random data will be generated, while ``/dev/urandom`` will generate pseudorandom data and return them immediately.
So ``/dev/urandom`` device is used more often because it is never blocked, but ``/dev/random`` is recommended when data has to be truly random and won't be vulnerable to RNG attacks. Ex. while generating private keys and other security data.

The current available entropy size in poll is stored in ``/proc/sys/kernel/random/entropy_avail`` file

.. code:: console

  $ cat /proc/sys/kernel/random/entropy_avail
  4012

Data from these devices can be read like any other binary file:

.. code:: console

  $ dd if=/dev/urandom bs=1 count=64|hexdump -C
  00000000  fb de 91 54 21 f5 5f a4  ef 9c a5 de 22 d3 ba 41  |...T!._....."..A|
  00000010  8b e5 3d 0e 26 7a 01 c2  b2 f6 6f 7a 9e 47 80 ce  |..=.&z....oz.G..|
  00000020  0c d2 49 c2 94 aa 70 95  ba d2 e7 19 8b 1c 01 a4  |..I...p.........|
  00000030  6b 2f 0f f2 ab 0b 89 3c  97 55 0c e9 b9 d5 c3 ae  |k/.....<.U......|
  00000040
  64+0 przeczytanych rekordów
  64+0 zapisanych rekordów
  skopiowane 64 bajty, 9,156e-05 s, 699 kB/s
  
  $ dd if=/dev/random bs=1 count=64|hexdump -C
  00000000  a3 0b 7d 8c 91 85 5d 30  18 fa f0 fe ae fb 89 42  |..}...]0.......B|
  00000010  c1 81 02 b7 20 62 b8 83  a3 8a 33 51 ee 83 1d 6f  |.... b....3Q...o|
  00000020  4d eb 6b e4 96 a4 9e c5  d8 bc 71 2a ec e7 27 5d  |M.k.......q*..']|
  00000030  2a 06 96 11 24 9b 88 13  3e 74 6f 16 f5 1b 8a 74  |*...$...>to....t|
  00000040
  64+0 przeczytanych rekordów
  64+0 zapisanych rekordów
  skopiowane 64 bajty, 0,00020758 s, 308 kB/s

It often happens, that some application needs a large amount of random data from ``/dev/random``, which leads to slow down its performance.
In that situation, we can use ``rngd``, which will fill entropy pool with data from hardware random number generator (if it is present)

/dev/full
---------

Last, but not least device that will be shown in this post is ``/dev/full``.
This is probably the most common device presented today.

When reading from the device it will return no data.

But, when we try to write anything, it will return ``ENOSPC`` error, which means that there is no free space on the volume.
This is usually used while testing the application's error handling in case of running out of space.

.. code:: console

   $ dd if=/dev/random of=/dev/full bs=1k count=1
   dd: error writing '/dev/full': No space left on device
   0+1 records in
   0+0 records out
   0 bytes copied, 0.00015115 s, 0.0 kB/s

Bonus
-----

In case of accidentally removing any device, we can easily recover it using documentation and ``mknod`` command.

For example, let's remove ``/dev/urandom`` device

.. code:: console

  [root@localhost bin]# ssh localhost
  Permission denied (publickey,gssapi-keyex,gssapi-with-mic).
  [root@localhost bin]# rm /dev/urandom
  rm: remove character special file ‘/dev/urandom’? y
  [root@localhost bin]# ssh localhost
  cannot read from /dev/urandom, No such file or directory
  [root@localhost bin]# mknod /dev/urandom c 1 9
  [root@localhost bin]# ssh localhost
  Permission denied (publickey,gssapi-keyex,gssapi-with-mic).

