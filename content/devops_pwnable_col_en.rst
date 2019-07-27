col - pwnable.kr
################

:keywords: linux, ctf, hacking, pwn, pwnable
:tags: linux, ctf, hacking. pwn, pwnable
:date: 2019-03-11
:Status: published
:slug: pwnable-col
:lang: en

Today we're going to solve collision task from `pwnable`_.

.. youtube:: hHwLdkF9j_Y

Analysis
--------

We can log in by ssh:

.. code-block:: console

   $ ssh col@pwnable.kr -p2222

with password ``guest``.

After log in, we can see three files:

.. code-block:: console

   fd@ubuntu:~$ ls -l
   total 16
   -r-sr-x--- 1 col_pwn col     7341 Jun 11  2014 col
   -rw-r--r-- 1 root    root     555 Jun 12  2014 col.c
   -r--r----- 1 col_pwn col_pwn   52 Jun 11  2014 flag

flag is located in ``flag`` file, but we cannot read it.
We can run ``col`` with has ``suid`` flag set and it can read the flag.

When we run ``col``:

.. code-block:: console

   fd@ubuntu:~$ ./col
   usage : ./col [passcode]

Let's take a look at the source code:

.. code-block:: c
   :linenos:

   #include <stdio.h>
   #include <string.h>
   unsigned long hashcode = 0x21DD09EC;
   unsigned long check_password(const char* p){
   	int* ip = (int*)p;
   	int i;
   	int res=0;
   	for(i=0; i<5; i++){
   		res += ip[i];
   	}
   	return res;
   }
   
   int main(int argc, char* argv[]){
   	if(argc<2){
   		printf("usage : %s [passcode]\n", argv[0]);
   		return 0;
   	}
   	if(strlen(argv[1]) != 20){
   		printf("passcode length should be 20 bytes\n");
   		return 0;
   	}
   
   	if(hashcode == check_password( argv[1] )){
   		system("/bin/cat flag");
   		return 0;
   	}
   	else
   		printf("wrong passcode.\n");
   	return 0;
   }

In lines 15-22 we can see, that application expect user to provide one argument with length of 20 bytes.

Next, in line 24, we can see, that result of function ``check_password`` with provided argument has to be equal ``hashcode`` with value ``0x21DD09EC``.

The main goal of this task is to analyze ``check_password`` function and find value of argument ``p``, which will produce value ``0x21DD09EC``.

Function ``check_password`` interpret 20 bytes char table as table of integer values.

We have to find the size of ``int`` integer to know how many integers are in table.

.. code-block:: console

   col@ubuntu:~$ file col
   col: setuid ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.6.24, BuildID[sha1]=05a10e253161f02d8e6553d95018bc82c7b531fe, not stripped

We can see, that this is a 32-bit application, so most likely integer has 32 bits size, so 4 bytes.

There we can calculate, that 20 bytes string with be interpreted as 5 elements integer array.

Next, we have to check bit numbering.

.. code-block:: console

   col@ubuntu:~$ readelf col -h
   ELF Header:
     Magic:   7f 45 4c 46 01 01 01 00 00 00 00 00 00 00 00 00
     Class:                             ELF32
     Data:                              2's complement, little endian
     Version:                           1 (current)
     OS/ABI:                            UNIX - System V
     ABI Version:                       0
     Type:                              EXEC (Executable file)
     Machine:                           Intel 80386
     Version:                           0x1
     Entry point address:               0x80483e0
     Start of program headers:          52 (bytes into file)
     Start of section headers:          4428 (bytes into file)
     Flags:                             0x0
     Size of this header:               52 (bytes)
     Size of program headers:           32 (bytes)
     Number of program headers:         9
     Size of section headers:           40 (bytes)
     Number of section headers:         30
     Section header string table index: 27

As we can see, there is ``little endian``.

Exploit
-------

To solve this task, we have to provide such string, that sum of 5 integer from that string will be equal to ``0x21DD09EC``.
To do so, we have to find 5 values witch sum will be ``0x21DD09EC`` and then write them up as a list of bytes.

I will use a python as a calculator.

First, let's divide result by 5, and find the flor of that number.
Then find the fifth number remainders.

.. code-block:: python

   >>> 0x21DD09EC/5.0
   113626824.8
   >>> 0x21DD09EC - 5 * 113626824
   4
   >>> hex(113626824)
   '0x6c5cec8'
   >>> hex(0x6c5cec8 + 4)
   '0x6c5cecc'
   >>> 4 * 0x6c5cec8 + 0x6c5cecc ==  0x21DD09EC
   True

As we can see, we have to pass ``0x6c5cec8`` four times, and ``0x6c5cecc`` one time

Because bytes are interpreted as little endian, we have to pass then in reverse order.

We will use bash to echo hexadecimal values

.. code-block:: console

   col@ubuntu:~$ ./col $(echo -ne "\xc8\xce\xc5\x06\xc8\xce\xc5\x06\xc8\xce\xc5\x06\xc8\xce\xc5\x06\xcc\xce\xc5\x06")
   daddy! I just managed to create a hash collision :)

And we've got a flag

.. _pwnable: https://pwnable.kr
