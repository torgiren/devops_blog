Hello World w Linuksie
######################

:keywords: linux, hello, world, tutorial, hacking, devops, assembler, elf
:tags: linux, hello, world, tutorial, hacking, devops, assembler, elf
:status: draft
:slug: hello-world
:date: 2020-07-16

W tym poście napiszę prosty program Hello World pod Linuksa.

Kod programu
------------

Zacznijmy od napisania wypisywania komunikatu na ekran.

| Użyjemy do tego wywołania systemowego ``write`` a następnie zwrócimy ``0``.
| Bazując na `liście syscalli`_, widzimy, że ``write`` ma number ``1``, natomiast ``exit`` ma number ``60``.

Następnie, sprawdzając w manualu dla tych ``syscall``-i widzimy, że ``write`` przyjmuje trzy argumenty, natomiast ``exit`` przyjmuje jeden.


.. code-block:: plain

    $ man 2 write
    ...
    ssize_t write(int fd, const void *buf, size_t count);
    ...

    $ man 2 exit
    ...
    void _exit(int status);
    ...

Natomiast w `abi`_ (str 137) widzimy, że numer ``syscall``-a należy podać w rejestrze ``rax``, natomiast argumenty kolejno w ``rdi``, ``rsi``, ``rdx``.

Jako ``fd`` podajemy ``1``, które odpowiada standardowemu wyjściu, jako ``buf`` podajemy adres do łańcucha znaków do wypisania oraz jako ``count`` podajemy długość tego łańcucha.

Co prowadzi nas do następującego pseudokodu:

.. code-block:: asm

   movl $1, %rax
   movl $1, %rdi
   movl string address, %rsi
   movl string lenght, %rdx
   syscall

   movl $60, $rax
   movl $0, $rdi
   syscall


Następnie, używając `opcodes`_, widzimy że instrukcja ``mov`` dla wartości ``immediate`` oraz rejestru 64bit ma ``opcode`` ``B8+r``

.. code-block:: plain

    MOV r16/32/64 imm16/32/64 B8+r

gdzie ``r`` oznacza numer  rejestru którego chcemy użyć, pamiętając że rejestry są numerowane od zera w kolejności ``rax``, ``rcx``, ``rdx``, ``rbx``, ``rsp``, ``rbp``, ``rsi`` oraz ``rdi``,

Natomiast ``syscall`` ma opcode: ``0F 05``

.. code-block:: plain

   SYSCALL RCX R11 SS ... 0F 05 D14 E

dlatego, aby zapisać nasz kod będziemy potrzebowali następujących instrukcji:

.. code-block:: plain

   b8 01 00 00 00
   ba 01 00 00 00
   be EA EA EA EA
   ba EB EB EB EB
   0F 05

   b8 3c 00 00 00
   ba 00 00 00 00
   0F 05

a za nimi umieścimy nasz napis ``Hello World`` czyli ``4865 6c6c 6f20 576f 726c 640a``

Zapisując to w jednej lini:

.. code-block:: plain

   b801 0000 00ba 0100 0000 beEA EAEA EAba EBEB EBEB 0F05 b83c 0000 00ba 0000 0000 0F05 4865 6c6c 6f20 576f 726c 640a

Nagłówek ELF
------------

| Teraz musimy przygotować nagłówek ``ELF``. Posłużymy się tutaj dokumentacją nagłówków `elf`_.
| Nie będę dokładnie opisywał wszystkich pól, a skupię się jedynie na tych które będą nam potrzebne do napisania aplikacji.

Nagłówek ``ELF`` ma następującą strukturę:

.. code-block:: c

   typedef struct {
       unsigned char e_ident[EI_NIDENT];
       uint16_t      e_type;
       uint16_t      e_machine;
       uint32_t      e_version;
       ElfN_Addr     e_entry;
       ElfN_Off      e_phoff;
       ElfN_Off      e_shoff;
       uint32_t      e_flags;
       uint16_t      e_ehsize;
       uint16_t      e_phentsize;
       uint16_t      e_phnum;
       uint16_t      e_shentsize;
       uint16_t      e_shnum;
       uint16_t      e_shstrndx;
   } ElfN_Ehdr;

która u nas przyjmie następujące wartości

``e_ident``:

    | Pierwsze cztery bajty mają wartość ``0x7f454c46``.
    | ``EI_CLASS`` dla 64bit przyjmuje wartość ``2``.
    | ``EI_DATA`` dla ``little endian`` przyjmuje wartość ``1``.
    | ``EI_VERSION`` musi być podane jako ``1``.
    | ``EI_OSABI`` dla systemów Linuks podajemy ``3``.
    | ``EI_ABIVERSION`` podajemy ``0``.
    | ``EI_PAD`` wypełnienie zerami do pełnych 16 bajtów, czyli ``16-9=7``
    | W efekcie otrzymamy: ``7f 45 4c 46 02 01 01 03 00 00 00 00 00 00 00 00``

``e_type``:

    | Dwubajtowa wartość określająca typ pliku.
    | Dla aplikacji wykonywalnej podajemy wartość ``0x0002``.

``e_machine``:

    | Dwubajtowa wartość która określa architekturę.
    | Dla x86_64 podajemy ``60``, czyli ``0x003e``.

``e_version``:

    | Czterobajtowa wartość określająca wersję.
    | Podajemy ``EV_CURRENT`` czyli ``0x00000001``.

``e_entry``:

    | Ośmiobajtowy adres początku wykonywania programu. Uzupełnimy go później.
    | Roboczo przyjmijmy wartość ``0xAAAAAAAAAAAAAAAA``.



``e_phoff``:

    | Ośmiobajtory offset w którym zaczynają się nagłówki programowe
    | Roboczo przyjmijmy wartość: ``0xBBBBBBBBBBBBBBBB``.

``e_shoff``:

    | Ośmiobajtory offset w którym zaczynają się nagłówki sekcji
    | Roboczo przyjmijmy wartość: ``0xCCCCCCCCCCCCCCCC``.

``e_flags``:

    | Czterobajtowa wartość określająca flagi.
    | Podajemy tutaj ``0x00000000``.

``e_ehsize``:

    | Dwubajtowa wartość określająca rozmiar tego nagłówka.
    | Dla systemu 64bit podajemy ``64`` czyli ``0x0040``

``e_phentsize``:

    | Dwubajtowa wartość określająca rozmiar pojedynczego wpisu w nagłówkach programowych
    | Dla 64bit podajemy wartość ``0x0038``.

``e_phnum``:

    | Dwubajtowa wartość określająca ilość nagłówków programowych
    | Roboczo przyjmijmy wartość ``0xDDDD``.

``e_shentsize``:

    | Dwubajtowa wartość określająca rozmiar pojedynczego wpisu w nagłówkach sekcji.
    | Dla 64bit podajemy wartość ``0x0040``.

``e_shnum``:

    | Dwubajtowa wartość określająca ilość nagłówków sekcji
    | Roboczo przyjmijmy wartość ``0xEEEE``.


e_shstrndx;

    | Dwubajtowa wartość określająca indeks nagłówka sekcji opisującego fragment przechowujący nazwy sekcji
    | Roboczo przyjmijmy wartość ``0xFFFF``.

Efekcie, nagłówek będzie wyglądał następująco:

.. code-block:: plain

   7f45 4c46 0201 0103 0000 0000 0000 0000 0200 3e00 0100 0000 AAAA AAAA AAAA AAAA BBBB BBBB BBBB BBBB CCCC CCCC CCCC CCCC 0000 0000 4000 3800 DDDD 4000 EEEE FFFF

Nagłówki programowe
-------------------

Następnie przygotujemy nagłówki programowe. Struktura każdego wpisu jest następująca:

.. code-block:: c

   typedef struct {
       uint32_t   p_type;
       uint32_t   p_flags;
       Elf64_Off  p_offset;
       Elf64_Addr p_vaddr;
       Elf64_Addr p_paddr;
       uint64_t   p_filesz;
       uint64_t   p_memsz;
       uint64_t   p_align;
   } Elf64_Phdr;

Stworzymy sobie jeden nagłówek programowy, który będzie ładował nasz kod wykonywalny do pamięci

``p_type``:

    | Czterobajtowa wartość przechowująca typ danego segmentu danych
    | W naszym przypadku, będzie to ``PT_LOAD`` czyli ``0x00000001``.

``p_flags``:

    | Czterobajtowa wartość przechowująca uprawnienia do ładowanego segmentu.
    | W naszym przypadku będzie to ``Read`` and ``Exec`` czyli ``0x00000005``.

``p_offset``:

    | Ośmiobajtowa wartość przechowująca offset w pliku od którego zaczniemy wczytywanie
    | Roboczo przyjmijmy ``0xABABABABABABABAB``.

``p_vaddr``:

    | Ośmiobajtowa wartość przechowująca adres pod który ma zostać załadowany segment
    | Roboczo przyjmijmy ``0xACACACACACACACAC``.

``p_paddr``:

    | Ośmiobajtowa wartość przechowująca fizyczny adres. Na systemach System V jest to ignorowane, ale zwykle podaje się to samo, co ``p_vaddr``.
    | Roboczo przyjmijmy ``0xACACACACACACACAC``.

``p_filesz``:

    | Ośmiobajtowa wartość przechowująca liczbę bajtów które mają zostać przeczytane z pliku
    | Roboczo przyjmijmy ``0xADADADADADADADAD``.

``p_memsz``:

    | Ośmiobajtowa wartość przechowująca liczbę bajtów które mają zostać zapisane do pamięci.
    | Przyjmijmy to samo co ``p_filesz`` ``0xADADADADADADADAD``.

``p_align``:

    | Ośmiobajtowa wartość przechowująca wartość dla wyrównania.
    | Przyjmijmy ``0x0000000000000000``.

W efekcie nagłówki programowe przyjmują postać:

.. code-block:: plain

   0100 0000 0500 0000 ABAB ABAB ABAB ABAB ACAC ACAC ACAC ACAC ACAC ACAC ACAC ACAC ADAD ADAD ADAD ADAD ADAD ADAD ADAD ADAD 0000 0000 0000 0000

Nagłówki sekcji
---------------

Następnie potrzebujemy dwóch sekcji.
Jednej na kod aplikacji, drugiej na nazwy sekcji.
Dodatkowo, na pierwszej pozycji należy umieścić pustą sekcje pustą.

Struktura wpisów sekcji jest następująca:

.. code-block:: c

   typedef struct {
       uint32_t   sh_name;
       uint32_t   sh_type;
       uint64_t   sh_flags;
       Elf64_Addr sh_addr;
       Elf64_Off  sh_offset;
       uint64_t   sh_size;
       uint32_t   sh_link;
       uint32_t   sh_info;
       uint64_t   sh_addralign;
       uint64_t   sh_entsize;
   } Elf64_Shdr;

Jako pierwszą przygotujemy sekcję z nazwami sekcji.

``sh_name``:

    | Czterobajtowa wartość określająca indeks nazwy sekcji na liście nazw sekcji. Pierwsza sekcja ma pustą nazwę, dlatego nazwa tej sekcji zaczyna się na pozycji ``1``.
    | W naszym przypadku będzie to ``0x00000001``.

``sh_type``:

    | Czterobajtowa wartość określająca typ danych w danej sekcji.
    | W naszym przypadku ``SHT_STRTAB`` czyli ``0x00000003``.

``sh_flags``:

    | Ośmiobajtowa wartość określająca flagi dla danej sekcji.
    | W naszym przypadku brak flag dla tej sekcji, czyli ``0x0000000000000000``.

``sh_addr``:

    | Ośmiobajtowa wartość określająca adres adres w pamięci w którym zaczyna znajduje się sekcja.
    | W naszym przypadku sekcja powinna być ładowana z pliku, czyli ``0x0000000000000000``.

``sh_offset``:

    | Ośmiobajtowa wartość określająca offset względem adresu
    | Roboczo przyjmijmy ``0xAEAEAEAEAEAEAEAE``.

``sh_size``:

    | Ośmiobajtowa wartość określająca rozmiar sekcji
    | Roboczo przyjmijmy ``0xAFAFAFAFAFAFAFAF``.


``sh_link``:

    | Czterobajtowa wartość, której zawartość jest różnie interpretowana w zależności o typu.
    | W naszym przypadku przyjmujemy ``0x00000000``

``sh_info``:

    | Czterobajtowa wartość, której zawartość jest różnie interpretowana w zależności o typu.
    | W naszym przypadku przyjmujemy ``0x00000000``

``sh_addralign``:

    | Ośmiobajtowa wartość przechowująca wartość dla wyrównania.
    | Przyjmujemy ``0x0000000000000000``.

``sh_entsize``:

    | Ośmiobajtowa wartość która jest używana, gdy sekcja opisuje tablicę o zadanym rozmiarze.
    | W naszym przypadku przyjmujemy ``0x0000000000000000``

W efekcie ten wpis będzie miał postać

.. code-block:: plain

   0001 0000 0300 0000 0000 0000 0000 0000 0000 0000 0000 0000 AEAE AEAE AEAE AEAE AFAF AFAF AFAF AFAF 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000

Następnie przygotujmy sekcję dla programu

``sh_name``:

    | Pierwsza sekcja ma pustą nazwę, druga sekcja ma nazwę ``.shstrtab``, dlatego ``.text`` zaczyna się na pozycji 12
    | W naszym przypadku będzie to ``0x0000000b``.

``sh_type``:

    | W naszym przypadku ``SHT_PROGBITS`` czyli ``0x00000001``.

``sh_flags``:

    | W naszym przypadku ``SHF_ALLOC`` oraz ``SHF_EXECINSTR``, czyli ``0x0000000000000006``.

``sh_addr``:

    | Roboczo przyjmijmy ``0xBABABABABABABABA``.

``sh_offset``:

    | Roboczo przyjmijmy ``0xBDBDBDBDBDBDBDBD``.

``sh_size``:

    | Roboczo przyjmijmy ``0xBCBCBCBCBCBCBCBC``.


``sh_link``:

    | Przyjmujemy ``0x00000000``

``sh_info``:

    | Przyjmujemy ``0x00000000``

``sh_addralign``:

    | Przyjmujemy ``0x0000000000000000``.

``sh_entsize``:

    | Przyjmujemy ``0x0000000000000000``.

Co w efekcie da nam:

.. code-block:: plain

   0b00 0000 0100 0000 0600 0000 0000 0000 BABA BABA BABA BABA BDBD BDBD BDBD BDBD BCBC BCBC BCBC BCBC 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000

Ostatnią rzeczą którą musimy przygotować, są nazwy sekcji.
Użyjemy domyślnych nazw ``.shstrtab`` oraz ``.text``

``002e 7368 7374 7274 6162 002e 7465 7874 0000``

Układ danych w pliku
--------------------

Spróbujmy teraz ułożyć wszystkie elementy w pliku.

| Nagłówek ELF będzie oczywiście na początku pliku.
| Następnie nagłówki programowe umieścimy pod adresem ``0x100``,
| Nagłówki sekcji pod adresem ``0x200``,
| kod programu pod adresem ``0x300``,
| a nazwy sekcji pod ``0x400``.


Tworzenie pliku
---------------

Znając położenie elementów w pliku, możemy podmienić placeholdery na właściwe wartości:

.. code-block:: plain

   EAEA EAEA: 0x400322 => 2203 4000
   EBEB EBEB: 0xC => 0C00 0000
   AAAA AAAA AAAA AAAA: 0x400300 => 0003 4000 0000 0000
   BBBB BBBB BBBB BBBB: 0x100 => 0001 0000 0000 0000
   CCCC CCCC CCCC CCCC: 0x200 => 0002 0000 0000 0000
   DDDD: 1 => 0100
   EEEE: 3 => 0300
   FFFF: 1 => 0100
   ABAB ABAB ABAB ABAB: 0003 0000 0000 0000
   ACAC ACAC ACAC ACAC: 0003 4000 0000 0000
   ADAD ADAD ADAD ADAD: 2e00 0000 0000 0000
   AEAE AEAE AEAE AEAE: 0004 0000 0000 0000
   AFAF AFAF AFAF AFAF: 1000 0000 0000 0000
   BABA BABA BABA BABA: 0003 4000 0000 0000
   BDBD BDBD BDBD BDBD: 0000 0000 0000 0000
   BCBC BCBC BCBC BCBC: 2e00 0000 0000 0000

Umieśćmy nasze dane w pliku (wejście zakańczamy enterem i sekwencją ``Ctrl-d``:

.. code-block:: console

   $ xxd -r -p - /tmp/dd #ELF
   7f45 4c46 0201 0103 0000 0000 0000 0000 0200 3e00 0100 0000 0003 4000 0000 0000 0001 0000 0000 0000 0002 0000 0000 0000 0000 0000 4000 3800 0100 4000 0300 0100
   $ xxd -r -p -s 0x100 - /tmp/dd #Program headers
   0100 0000 0500 0000 0003 0000 0000 0000 0003 4000 0000 0000 0003 4000 0000 0000 2e00 0000 0000 0000 2e00 0000 0000 0000 0000 0000 0000 0000
   $ xxd -r -p -s 0x200 - /tmp/dd #Section header null
   0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
   $ xxd -r -p -s 0x240 - /tmp/dd #Section header text
   0100 0000 0300 0000 0000 0000 0000 0000 0000 0000 0000 0000 0004 0000 0000 0000 1000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
   $ xxd -r -p -s 0x280 - /tmp/dd #Section header strtab
   0b00 0000 0100 0000 0600 0000 0000 0000 0003 4000 0000 0000 0000 0000 0000 0000 2e00 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
   $ xxd -r -p -s 0x300 - /tmp/dd #Code
   b801 0000 00ba 0100 0000 be22 0340 00ba 0C00 0000 0F05 b83c 0000 00ba 0000 0000 0F05 4865 6c6c 6f20 576f 726c 640a
   $ xxd -r -p -s 0x400 - /tmp/dd #Section names
   002e 7368 7374 7274 6162 002e 7465 7874 0000

Otrzymany plik powinien mieć postać:

.. code-block:: hexdump

   00000000  7f 45 4c 46 02 01 01 03  00 00 00 00 00 00 00 00  |.ELF............|
   00000010  02 00 3e 00 01 00 00 00  00 03 40 00 00 00 00 00  |..>.......@.....|
   00000020  00 01 00 00 00 00 00 00  00 02 00 00 00 00 00 00  |................|
   00000030  00 00 00 00 40 00 38 00  01 00 40 00 03 00 01 00  |....@.8...@.....|
   00000040  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
   *
   00000100  01 00 00 00 05 00 00 00  00 03 00 00 00 00 00 00  |................|
   00000110  00 03 40 00 00 00 00 00  00 03 40 00 00 00 00 00  |..@.......@.....|
   00000120  2e 00 00 00 00 00 00 00  2e 00 00 00 00 00 00 00  |................|
   00000130  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
   00000140  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
   *
   00000240  01 00 00 00 03 00 00 00  00 00 00 00 00 00 00 00  |................|
   00000250  00 00 00 00 00 00 00 00  00 04 00 00 00 00 00 00  |................|
   00000260  10 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
   00000270  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
   00000280  0b 00 00 00 01 00 00 00  06 00 00 00 00 00 00 00  |................|
   00000290  00 03 40 00 00 00 00 00  00 00 00 00 00 00 00 00  |..@.............|
   000002a0  2e 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
   000002b0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
   *
   00000300  b8 01 00 00 00 ba 01 00  00 00 be 22 03 40 00 ba  |...........".@..|
   00000310  0c 00 00 00 0f 05 b8 3c  00 00 00 ba 00 00 00 00  |.......<........|
   00000320  0f 05 48 65 6c 6c 6f 20  57 6f 72 6c 64 0a 00 00  |..Hello World...|
   00000330  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
   *
   00000400  00 2e 73 68 73 74 72 74  61 62 00 2e 74 65 78 74  |..shstrtab..text|
   00000410  00 00                                             |..|
   00000412

Oraz być uruchamialny:

.. code-block:: console

   torgiren@redraptor /tmp $ chmod +x /tmp/dd 
   torgiren@redraptor /tmp $ /tmp/dd 
   Hello World


.. _liście syscalli: https://github.com/torvalds/linux/blob/master/arch/x86/entry/syscalls/syscall_64.tbl
.. _abi: https://software.intel.com/sites/default/files/article/402129/mpx-linux64-abi.pdf
.. _opcodes: http://ref.x86asm.net/coder64-abc.html
.. _elf: https://linux.die.net/man/5/elf
