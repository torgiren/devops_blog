Pushd/Popd
######################################

:keywords: linux, devops, bash, stack
:tags: linux, devops, bash, stack
:status: published
:slug: pushd
:lang: en
:date: 2020-05-11

In this post, I will show bash commands ``pushd`` and ``popd``.

.. youtube:: 1bGq9bYbzyI

`Bash` shell has one functionality that is not widely known - this functionality is directory stack.

As the name suggests, it's a stack where one can store directories, and on top of that stack is stored current directory.

Before we learn how this stack works, let's take a look at the commands to operate it:

- ``pushd`` - is used for adding directories to the stack
- ``popd`` - is used for removing directories from the stack
- ``dirs`` - is used for displaying directories on the stack

We're going to learn how to use stack but examples :)

First, let's display the current stack content:

.. code-block:: console

   torgiren@redraptor ~ $ dirs -v
    0  ~
   torgiren@redraptor ~ $ cd /tmp
   torgiren@redraptor /tmp $ dirs -v
    0  /tmp

We can see, that ``dirs -v`` prints out the content of the stack, which but the default has only one item - current directory

Next, let's add some directory on top of the stack

.. code-block:: console

   torgiren@redraptor /tmp $ pushd /proc/
   /proc /tmp
   torgiren@redraptor /proc $ dirs -v
    0  /proc
    1  /tmp

We can see, that ``/proc`` directory was added on top and ``/tmp`` was moved to the second position.
Also, the current directory was changed to ``/proc``.
As I said before, the current directory is on top of the stack, that's why adding ``/proc`` on top we changed the current directory

After the traditional change directory, we can see that:

.. code-block:: console

   torgiren@redraptor /proc $ cd /sys
   torgiren@redraptor /sys $ dirs -v
    0  /sys
    1  /tmp

the top element was changed

Next, let's try to pop the top element:

.. code-block:: console

   torgiren@redraptor /sys $ popd
   /tmp
   torgiren@redraptor /tmp $ dirs -v
    0  /tmp

what happened here...

``popd`` command popped the top element, that's why the second element became the top element and that changed current directory to ``/tmp``.

With this knowledge, we can move to real-life example (one of the two I use most often)

.. code-block:: console

   torgiren@redraptor /tmp $ pushd .
   /tmp /tmp
   torgiren@redraptor /tmp $ dirs -v
    0  /tmp
    1  /tmp
   torgiren@redraptor /tmp $ cd /etc
   torgiren@redraptor /etc $ cd conf.d
   torgiren@redraptor /etc/conf.d $ pwd
   /etc/conf.d
   torgiren@redraptor /etc/conf.d $ cd ..
   torgiren@redraptor /etc $ cd init.d/
   torgiren@redraptor /etc/init.d $ popd
   /tmp
   torgiren@redraptor /tmp $ dirs -v
    0  /tmp

what's going on here...

When I was in ``/tmp`` directory, I pushed on the stack the current directory - ``/tmp``.
As a result, I had ``/tmp`` twice on the stack.
Next, I changed the directories to ``/etc``, ``/ecp/conf.d``, ``/etc/init.d``.
As we know, ``cd`` change only the top element, what that's why there's ``/tmp`` still on position 1.
After finishing work in ``/etc`` directories, I used ``popd`` to pop the top element, and position 1 became position 0, so I backed to the ``/tmp`` directory.
It's the improved version of ``cd -``, because ``cd -`` allows to back only to the last directory and using stack allows to make any number of dir changes and then back to remembered position.

We can also use ``pushd -n`` to add items on the stack without changing the current directory.
It is added to the second position then.

.. code-block:: console

   torgiren@redraptor /tmp $ cd /tmp/
   torgiren@redraptor /tmp $ mkdir -p pushd/a1
   torgiren@redraptor /tmp $ mkdir -p pushd/a2
   torgiren@redraptor /tmp $ mkdir -p pushd/a3
   torgiren@redraptor /tmp $ cd pushd/
   torgiren@redraptor /tmp/pushd $ touch a1/test.txt
   torgiren@redraptor /tmp/pushd $ touch a1/test2.txt
   torgiren@redraptor /tmp/pushd $ touch a1/test3.txt
   torgiren@redraptor /tmp/pushd $ pushd -n a1
   /tmp/pushd a1
   torgiren@redraptor /tmp/pushd $ pushd -n a2
   /tmp/pushd a2 a1
   torgiren@redraptor /tmp/pushd $ pushd -n a3
   /tmp/pushd a3 a2 a1
   torgiren@redraptor /tmp/pushd $ dirs -v
    0  /tmp/pushd
    1  a3
    2  a2
    3  a1


With stack like this, we can go to the second functionality most often used by me.

Let's say we want to move ``test2.txt`` file to ``a2`` directory, and ``test3.txt`` to ``a3``.
Instead of the standard ``mv a1/test2.txt a2`` we can do:

.. code-block:: console

   torgiren@redraptor /tmp/pushd $ mv ~3/test2.txt ~2/ -iv
   przemianowany 'a1/test2.txt' -> 'a2/test2.txt'
   torgiren@redraptor /tmp/pushd $ mv ~3/test3.txt ~1/ -iv
   przemianowany 'a1/test3.txt' -> 'a3/test3.txt'


At first glance it can not seems like a big improvement to standard ``mv``, but let's take a look at a real-life example:

.. code-block:: console

   torgiren@redraptor /tmp/pushd $ dirs -v
    0  /tmp/pushd
   torgiren@redraptor /tmp/pushd $ pushd .
   /tmp/pushd /tmp/pushd
   torgiren@redraptor /tmp/pushd $ dirs -v
    0  /tmp/pushd
    1  /tmp/pushd
   torgiren@redraptor /tmp/pushd $ cd /etc/
   torgiren@redraptor /etc $ cd conf.d/
   torgiren@redraptor /etc/conf.d $ cd ..
   torgiren@redraptor /etc $ cd init.d/
   torgiren@redraptor /etc/init.d $ cp mdadm ~1/a3/ -iv
   'mdadm' -> '/tmp/pushd/a3/mdadm'
   torgiren@redraptor /etc/init.d $ dirs -v
    0  /etc/init.d
    1  /tmp/pushd
   torgiren@redraptor /etc/init.d $ popd
   /tmp/pushd
   torgiren@redraptor /tmp/pushd $ dirs -v
    0  /tmp/pushd

why I find this example to be useful?
Because at any stage I don't need to know the exact file path of source nor destination.
When talking about the destination, we store current directory on stack, and with source, we can navigate between directories looking for the expected file.
And then, in an easy way we can return to the primary directory.


The next thing we can do with the directory stack is to rotate it.

It lets you change directories without removing them from the stack.
Direction and step that the stack should be rotated are passed as argument in the format ``+/-num`` instead of a directory.

.. code-block:: console

   torgiren@redraptor /tmp/pushd/a2 $ pushd -n /tmp/pushd/a3
   /tmp/pushd/a2 /tmp/pushd/a3
   torgiren@redraptor /tmp/pushd/a2 $ pushd -n /tmp/pushd/a2
   /tmp/pushd/a2 /tmp/pushd/a2 /tmp/pushd/a3
   torgiren@redraptor /tmp/pushd/a2 $ cd /tmp/pushd/a1/
   torgiren@redraptor /tmp/pushd/a1 $ dirs -v
    0  /tmp/pushd/a1
    1  /tmp/pushd/a2
    2  /tmp/pushd/a3
   torgiren@redraptor /tmp/pushd/a1 $ pwd
   /tmp/pushd/a1
   torgiren@redraptor /tmp/pushd/a1 $ pushd +1
   /tmp/pushd/a2 /tmp/pushd/a3 /tmp/pushd/a1
   torgiren@redraptor /tmp/pushd/a2 $ pwd
   /tmp/pushd/a2
   torgiren@redraptor /tmp/pushd/a2 $ pushd +1
   /tmp/pushd/a3 /tmp/pushd/a1 /tmp/pushd/a2
   torgiren@redraptor /tmp/pushd/a3 $ pwd
   /tmp/pushd/a3
   torgiren@redraptor /tmp/pushd/a3 $ pushd +1
   /tmp/pushd/a1 /tmp/pushd/a2 /tmp/pushd/a3


The last but one thing which we can do with the stack is to remove specified elements from it.
Because ``popd`` let us remove not only the top element but also any other.
To specify the item to remove we have to specify it by passing number with direction ``+`` or ``-`` which means that we want to count from the top or the bottom.
Ex. let's remove from stack elements ``a5``, ``a15``, ``a20``, ``a1``, ``a19``.

.. code-block:: console

   torgiren@redraptor /tmp/pushd $ for i in $(seq 1 20); do pushd -n a$i; done
   /tmp/pushd a1
   /tmp/pushd a2 a1
   /tmp/pushd a3 a2 a1
   /tmp/pushd a4 a3 a2 a1
   /tmp/pushd a5 a4 a3 a2 a1
   /tmp/pushd a6 a5 a4 a3 a2 a1
   /tmp/pushd a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a12 a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a13 a12 a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a14 a13 a12 a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a15 a14 a13 a12 a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a16 a15 a14 a13 a12 a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a17 a16 a15 a14 a13 a12 a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a18 a17 a16 a15 a14 a13 a12 a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a19 a18 a17 a16 a15 a14 a13 a12 a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a20 a19 a18 a17 a16 a15 a14 a13 a12 a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   torgiren@redraptor /tmp/pushd $ dirs -v
    0  /tmp/pushd
    1  a20
    2  a19
    3  a18
    4  a17
    5  a16
    6  a15
    7  a14
    8  a13
    9  a12
   10  a11
   11  a10
   12  a9
   13  a8
   14  a7
   15  a6
   16  a5
   17  a4
   18  a3
   19  a2
   20  a1
   torgiren@redraptor /tmp/pushd $ popd -4 # a5
   /tmp/pushd a20 a19 a18 a17 a16 a15 a14 a13 a12 a11 a10 a9 a8 a7 a6 a4 a3 a2 a1
   torgiren@redraptor /tmp/pushd $ popd +6 # a15
   /tmp/pushd a20 a19 a18 a17 a16 a14 a13 a12 a11 a10 a9 a8 a7 a6 a4 a3 a2 a1
   torgiren@redraptor /tmp/pushd $ popd +1 # a20
   /tmp/pushd a19 a18 a17 a16 a14 a13 a12 a11 a10 a9 a8 a7 a6 a4 a3 a2 a1
   torgiren@redraptor /tmp/pushd $ popd -0 # a1
   /tmp/pushd a19 a18 a17 a16 a14 a13 a12 a11 a10 a9 a8 a7 a6 a4 a3 a2
   torgiren@redraptor /tmp/pushd $ popd +1 # a19
   /tmp/pushd a18 a17 a16 a14 a13 a12 a11 a10 a9 a8 a7 a6 a4 a3 a2


And the last operation we can find useful I to clear the stack leaving only current directory.
We use ``dirs -c`` command to achieve that

.. code-block:: console

   torgiren@redraptor /tmp/pushd $ dirs -v
    0  /tmp/pushd
    1  a18
    2  a17
    3  a16
    4  a14
    5  a13
    6  a12
    7  a11
    8  a10
    9  a9
   10  a8
   11  a7
   12  a6
   13  a4
   14  a3
   15  a2
   torgiren@redraptor /tmp/pushd $ dirs -c
   torgiren@redraptor /tmp/pushd $ dirs -v
    0  /tmp/pushd



