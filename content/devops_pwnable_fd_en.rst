fd - pwnable.kr
###############

:keywords: linux, ctf, hacking, pwn, pwnable
:tags: linux, ctf, hacking, pwn, pwnable
:date: 2019-06-02
:Status: published
:slug: pwnable-fd
:lang: en

In this post we're going to solve ``fd`` challenge from `pwnable`_.

.. youtube:: EtMYdsvIRmo

We can log in by ssh:

.. code-block:: console

   $ ssh fd@pwnable.kr -p2222

with password ``guest``.

After log in, we can see three files:

.. code-block:: console

   fd@ubuntu:~$ ls -l
   total 16
   -r-sr-x--- 1 fd_pwn fd   7322 Jun 11  2014 fd
   -rw-r--r-- 1 root   root  418 Jun 11  2014 fd.c
   -r--r----- 1 fd_pwn root   50 Jun 11  2014 flag

The flag is placed in ``flag`` file, but we cannot access it.
But we can run ``fd`` application, which has set ``suid`` flag, what allows it to read the flag.

After execute ``fd``:

.. code-block:: console

   fd@ubuntu:~$ ./fd
   pass argv[1] a number

So, we have to check out, what ``fd`` do.
The source code is located in ``fd.c``

.. code-block:: c
   :linenos:

   #include <stdio.h>
   #include <stdlib.h>
   #include <string.h>
   char buf[32];
   int main(int argc, char* argv[], char* envp[]){
   	if(argc<2){
   		printf("pass argv[1] a number\n");
   		return 0;
   	}
   	int fd = atoi( argv[1] ) - 0x1234;
   	int len = 0;
   	len = read(fd, buf, 32);
   	if(!strcmp("LETMEWIN\n", buf)){
   		printf("good job :)\n");
   		system("/bin/cat flag");
   		exit(0);
   	}
   	printf("learn about Linux file IO\n");
   	return 0;
   
   }

As we can see, lines 6-8 forces application to check there is a least one argument.

Next, in line 10, we can see, that it initialize ``fd`` variable with passed argument, cast to ``int`` type, and next substituted with hexadecimal ``0x1234``.

In line 12, we can see, that ``fd`` is used as ``file descriptor`` in ``read`` function, and the read data are stored in ``buf``.

At last, in line 13 we compare read buffer with string ``LETMEWIN``.

Because, there are the default file descriptors:

- ``0``: standard in
- ``1``: standard out
- ``2``: standard error out

The easies way to read buffer will be using existing input - keyboard.

To get ``fd`` value equal to  ``0``, we have to pass value ``0x1234`` to command line argument, but in decimal.

Personally, I prefer using python to calculate hex <=> decimal values

.. code-block:: console

   fd@ubuntu:~$ python
   Python 2.7.12 (default, Nov 12 2018, 14:36:49) 
   [GCC 5.4.0 20160609] on linux2
   Type "help", "copyright", "credits" or "license" for more information.
   >>> 0x1234
   4660

Next, we have to run ``fd`` with argument ``4660`` and type ``LETMEWIN``.

.. code-block:: console

   fd@ubuntu:~$ ./fd 4660
   LETMEWIN
   good job :)
   mommy! I think I know what a file descriptor is!!

And we've got the flag

.. _pwnable: https://pwnable.kr
