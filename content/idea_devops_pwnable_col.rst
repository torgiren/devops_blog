col - pwnable.kr
################

:keywords: linux, ctf, hacking, pwn, pwnable
:tags: linux, ctf, hacking. pwn, pwnable
:date: 2019-03-11
:Status: draft
:slug: pwnable-col

W tym poście rozwiążemy sobie zadanie ``col`` ze strony `pwnable`_.

Analiza wstępna
---------------

Aby zalogować się do zadania wykonujemy:

.. code-block:: console

   $ ssh col@pwnable.kr -p2222

a jako hasło podajemy ``guest``.

Po zalogowaniu się widzimy 3 pliki

.. code-block:: console

   fd@ubuntu:~$ ls -l
   total 16
   -r-sr-x--- 1 col_pwn col     7341 Jun 11  2014 col
   -rw-r--r-- 1 root    root     555 Jun 12  2014 col.c
   -r--r----- 1 col_pwn col_pwn   52 Jun 11  2014 flag


flaga znajduje się w pliku ``flag``, natomiast nie mamy do niego dostępu.
Mamy natomiast możliwość wykonania programu ``col``, który ma ustawiony ``suid`` pozwalający na odczyt flagi.

Uruchomienie aplikacji daje następujące wyjście:

.. code-block:: console

   fd@ubuntu:~$ ./col
   usage : ./col [passcode]


Dlatego sprawdźmy co robi ta aplikacja.
Kod programu znajduje się w pliku ``col.c``

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

Patrząc na linie 15-22 widzimy, że aplikacja oczekuje co najmniej jednego argumentu oraz że pierwszy argument będzie miał długość dokładnie 20 znaków.

Następnie w linii 25 widzimy, że wynik funkcji ``check_password`` uruchomiony z podanych przez nas argumentem, musi być równy globalnej zmiennej ``hashcode`` równej ``0x21DD09EC``.

Głównym celem tego zadania jest analiza funkcji ``check_password`` oraz znalezienie takiego argumentu ``p``, aby wynik równy był ``0x21DD09EC``.

Funkcja ``check_password`` interpretuje podany 20-bajtowy ciąg znaków, jako zmienne typu ``int``.

Aby wiedzieć jaki rozmiar ma zmienna typu ``int``, należy sprawdzić jak została skompilowana aplikacja.

.. code-block:: console

   col@ubuntu:~$ file col
   col: setuid ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.6.24, BuildID[sha1]=05a10e253161f02d8e6553d95018bc82c7b531fe, not stripped

Widzimy, że ``col`` jest aplikacją 32-bitową, a to znaczy, że najprawdopodobniej zmienna typu ``int`` będzie miała rozmiar 32 bitów, czyli 4 bajtów.

Wynika z tego, że 20 bajtowy ciąg znaków, będący argumentem funkcji ``check_password``, może zostać zinterpretowany jako pięć 4-bajtowych wartości typu ``int``.

Dodatkowo, należy sprawdzić w jakiej konwencji są zapisywane bity w pamięci.
Osobiście nie spotkałem się z konwencją *big endian* w aplikacjach, lecz aby zrobić wszystko po kolei, należy sprawdzić użytą konwencję:

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

Widzimy, że została zastosowana ``little endian``.
Więcej o ``little endian`` możesz przeczytać/obejrzeć tutaj <TODO!!!!!!!>

Exploit
-------

Aby warunek poprawności hasła został spełniony, suma 5 liczb całkowitych otrzymanych z podanego *string*-a musi być równa ``0x21DD09EC``.
Jednym ze sposobów aby to osiągnąć, jest znalezienie znalezienie 5 liczb których suma da taką wartość, a następnie zapisanie ich w postaci pojedynczych bajtów.

W celu poszukiwania liczb użyjemy pythona, gdyż dobrze sprawdza się jako kalkulator.
na początku próbujemy podzielić szukaną liczbę przez 5, a gdy to się nie uda, to szukamy największej liczby, mniejszej od naszego wyniku, która będzie podzielna przez 5

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

Z powyższego widzimy, że potrzebujemy przekazać cztery wartości ``0x6c5cec8`` oraz jedną o ``4`` większą, czyli ``0x6c5cecc`` .

Ponieważ aplikacja jest w konwencji *little endian*, bajty należy podawać od końca (więcej o tym można przeczytać TUTAJ!!! TODO)

Aby wypisać konkretne bity, użyjemy ``echo`` z ``bash`` i podamy bajty *od tył* i przekażemy wynik do aplikacji ``col``, jako pierwszy argument.

.. code-block:: console

   col@ubuntu:~$ ./col $(echo -ne "\xc8\xce\xc5\x06\xc8\xce\xc5\x06\xc8\xce\xc5\x06\xc8\xce\xc5\x06\xcc\xce\xc5\x06")
   daddy! I just managed to create a hash collision :)

I otrzymaliśmy szukaną flagę.

.. _pwnable: https://pwnable.kr
