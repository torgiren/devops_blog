How it is with little-endian
############################

:keywords: linux, hacking, little-endian, memory
:tags: linux, hacking, little-endian, memory
:date: 2019-07-29
:Status: published
:slug: little-endian
:lang: en

In this post I'm going to tell something about little endian.

.. youtube:: k0-BCbqMN9g

Let's start with earthquake
---------------------------

.. code-block:: C

    int main()
    {
        long int x=0x4142434445464748;
    }

.. code-block:: console

   $ gcc -g main.c -o main
   $ gdb main
   (gdb)$ break main
   (gdb)$ layout src
   (gdb)$ r
   (gdb)$ s

In 64bit OS, long ing has 8 bytes

So, let's print it

.. code-block:: console

  (gdb)$ x/1gx &x
  0x7fffffffdca8: 0x4142434445464748

But, 64bits is also 2x32 bit

.. code-block:: console

  (gdb)$ x/2wx &x
  0x7fffffffdca8: 0x45464748	0x41424344

And it's 4x16

.. code-block:: console

  (gdb)$ x/4hx &x
  0x7fffffffdca8: 0x4748  0x4546  0x4344  0x4142

as well as 8x8 bit

.. code-block:: console

  (gdb)$ x/8bx &x
  0x7fffffffdca8: 0x48    0x47    0x46    0x45    0x44    0x43    0x42    0x41

But what's with the order?

and let the tension rise
------------------------

To understand this, we have to know, how bits are store in memory.

There are two conventions: ``bit endian`` and ``little endian``.

In ``big endian`` most significant bit is stored as a first bit, and least significant as the last, and in ``little endian`` is the opposite - least significant is stored as first.

``Big endian`` is used in processors like SPARC and PowerPC, and ``little endian`` in x86 and many more.

Normal order? reverse order? or mixed?
--------------------------------------

If we take a look at values printed in ``gdb``, we can see, that the value is printed as whole 64 bit value it is printes *as it is*.
But, if we print it per byte, we get value in reverse order.
And, if we print it by word or half word, we got mixed order.

To understand this, we have to print our value in binary system.

Value ``0x4142434445464748`` in binary is:

  ``0100000101000010010000110100010001000101010001100100011101001000``

because of ``little-endian``, most significant bit has to be the last one, so we have to reverse this value:

  ``0001001011100010011000101010001000100010110000100100001010000010``

That how the value will be stored in memory.

Then why do we once see it correctly, once mixing, and once from behind?

To ease reading the bits, let's group them into bytes

  ``00010010 11100010 01100010 10100010 00100010 11000010 01000010 10000010``

When we read the value as 64 bit, OS read the whole 64 bit and interpret it (reverse bits and print)

But, when we read 2x32 bits, OS read first 32 bit, interpret and print them, and then read the following 32 bits.

  ``(00010010 11100010 01100010 10100010) (00100010 11000010 01000010 10000010)``

Every of this two 32 bit values are interpretes seperately, that we OS reverse order of the bits for every value.

  ``(01000101 01000110 01000111 01001000) (01000001 01000010 01000011 01000100)``

and then print them

  ``(0x45464748) (0x41424344)``

so, that the result we got in gdb.


This is the same for 4x16 bits...

  ``(00010010 11100010) (01100010 10100010) (00100010 11000010) (01000010 10000010)``

after inversion

  ``(01000111 01001000) (01000101 01000110) (01000011 01000100) (01000001 01000010)``

and in hexadecimal

  ``(0x4748) (0x4546) (0x4344) (0x4142)``

And the last one, per byte

  ``(00010010) (11100010) (01100010) (10100010) (00100010) (11000010) (01000010) (10000010)``
 
invert

  ``(01001000) (01000111) (01000110) (01000101) (01000100) (01000011) (01000010) (01000001)``

print

  ``(0x48) (0x47) (0x46) (0x45) (0x44) (0x43) (0x42) (0x41)``


Example
-------

In `col`_ task, we had to preapre integer value using only writing per byte.

The expected value was ``0x6c5cec8``, and user could only write data by char array.
That's why, we have to know, how the value will be stored in memory

``0x6c5cec8`` will be stored as:

  ``(0xc8) (0xce) (0xc5) (0x06)``

and, we had to pass the following string

  ``$ echo -ne "\xc8\xce\xc5\x06"``

.. _col: /pwnable-col-en.html
