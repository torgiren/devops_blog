flag - pwnable.kr
#################

:keywords: linux, ctf, hacking, pwn, pwnable
:tags: linux, ctf, hacking. pwn, pwnable
:date: 2019-03-11
:Status: draft
:slug: pwnable-flag

W tym poście rozwiążemy sobie zadanie ``flag`` ze strony `pwnable`_.

Aby pobrać program który zawiera flagę, należy wykonać polecenie:

.. code-block:: console

   $ wget http://pwnable.kr/bin/flag

Przy próbie deasemblacji aplikacji, widzimy, że ``objdump`` nie jest w stanie pokazać zawartości programu:

.. code-block:: console

   $ objdump -D flag

   flag:     file format elf64-x86-64

Takie zachowanie może występować zarówno przy błędnej zawartości pliku jak również po spakowaniu programu przy użyciu *packera*.
Jednym ze sposób na znalezienie oznak użycia *packer*-a, jest przeszukanie pliku w poszukiwaniu fraz *pack*:

.. code-block:: console

   $ strings flag|grep -i pack
   $Info: This file is packed with the UPX executable packer http://upx.sf.net $

Z powyższego widać, że został użyty packer ``UPX``.
Aby rozpakować program, użyjemy polecenia ``upx``:

.. code-block:: console

   $ upx -d flag
                          Ultimate Packer for eXecutables
                             Copyright (C) 1996 - 2018
   UPX 3.95        Markus Oberhumer, Laszlo Molnar & John Reiser   Aug 26th 2018

           File size         Ratio      Format      Name
      --------------------   ------   -----------   -----------
       883745 <-    335288   37.94%   linux/amd64   flag

   Unpacked 1 file.

W tej chwili jesteśmy w stanie zdisasemblować kod aplikacji oraz wyświetlić zawartość funkcji ``main``.

.. code-block:: console

   $ ./flag
   I will malloc() and strcpy the flag there. take it.

   $ objdump -D flag

   [...]
   0000000000401164 <main>:
     401164:       55                      push   %rbp
     401165:       48 89 e5                mov    %rsp,%rbp
     401168:       48 83 ec 10             sub    $0x10,%rsp
     40116c:       bf 58 66 49 00          mov    $0x496658,%edi
     401171:       e8 0a 0f 00 00          callq  402080 <_IO_puts>
     401176:       bf 64 00 00 00          mov    $0x64,%edi
     40117b:       e8 50 88 00 00          callq  4099d0 <__libc_malloc>
     401180:       48 89 45 f8             mov    %rax,-0x8(%rbp)
     401184:       48 8b 15 e5 0e 2c 00    mov    0x2c0ee5(%rip),%rdx        # 6c2070 <flag>
     40118b:       48 8b 45 f8             mov    -0x8(%rbp),%rax
     40118f:       48 89 d6                mov    %rdx,%rsi
     401192:       48 89 c7                mov    %rax,%rdi
     401195:       e8 86 f1 ff ff          callq  400320 <.plt+0x10>
     40119a:       b8 00 00 00 00          mov    $0x0,%eax
     40119f:       c9                      leaveq
     4011a0:       c3                      retq
   [...]

Po uruchomieniu aplikacji widzimy, że aplikacja robi ``malloc`` a następnie ``strcpy``.
Z kodu, widzimy, że ``malloc`` wykonywany jest pod adresem ``0x40117b``, następnie zostają ustawiane parametry i wykonywana kolejna funkcja.
Możemy przypuszczać, że jest to funkcja ``strcpy``.
Ponieważ aplikacja wykonuje ``strcpy`` flagi, dlatego szukana flaga musi zostać przekazana przez argumenty.
AMD64 ABI mówi, że nasz **source argument** będzie umieszczony w ``rsi``.

Do odczytania flagi użyjemy ``gdb``.
Ustawimy ``breakpoint`` tuż przed funkcją ``strcpy`` na następnie odczytać zawartość pamięci pod adresem przechowywanym w rejestrze ``rsi``.

.. code-block:: console

   $ gdb flag
   (gdb) break *0x401195
   Breakpoint 1 at 0x401195
   (gdb) r
   Starting program: /tmp/flag
   I will malloc() and strcpy the flag there. take it.

   Breakpoint 1, 0x0000000000401195 in main ()
   (gdb) info reg
   rax            0x6c96b0            7116464
   rbx            0x401ae0            4201184
   rcx            0x8                 8
   rdx            0x496628            4810280
   rsi            0x496628            4810280
   rdi            0x6c96b0            7116464
   rbp            0x7fffffffd640      0x7fffffffd640
   rsp            0x7fffffffd630      0x7fffffffd630
   r8             0x1                 1
   r9             0x3                 3
   r10            0x22                34
   r11            0x0                 0
   r12            0x401a50            4201040
   r13            0x0                 0
   r14            0x0                 0
   r15            0x0                 0
   rip            0x401195            0x401195 <main+49>
   eflags         0x206               [ PF IF ]
   cs             0x33                51
   ss             0x2b                43
   ds             0x0                 0
   es             0x0                 0
   fs             0x0                 0
   gs             0x0                 0
   (gdb) x/10s $rsi
   0x496628:	"UPX...? sounds like a delivery service :)"
   0x496652:	""
   0x496653:	""
   0x496654:	""
   0x496655:	""
   0x496656:	""
   0x496657:	""
   0x496658:	"I will malloc() and strcpy the flag there. take it."
   0x49668c:	"FATAL: kernel too old\n"
   0x4966a3:	"/dev/urandom"

I otrzymaliśmy szukaną flagę

.. _pwnable: https://pwnable.kr
