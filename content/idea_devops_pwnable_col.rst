col - pwnable.kr
################

:keywords: linux, ctf, hacking, pwn, pwnable
:tags: linux, ctf, hacking. pwn, pwnable
:date: 2019-03-11
:Status: draft
:slug: pwnable-col

W tym poście rozwiążemy sobie zadanie ``col`` ze strony `pwnable`_.

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

.. _pwnable: https://pwnable.kr
