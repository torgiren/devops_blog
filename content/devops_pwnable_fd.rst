fd - pwnable.kr
###############

:keywords: linux, ctf, hacking, pwn, pwnable
:tags: linux, ctf, hacking. pwn, pwnable
:date: 2019-06-02
:Status: published
:slug: pwnable-fd

W tym poście rozwiążemy sobie zadanie ``fd`` ze strony `pwnable`_.

.. youtube:: EtMYdsvIRmo

Aby zalogować się do zadania wykonujemy:

.. code-block:: console

   $ ssh fd@pwnable.kr -p2222

a jako hasło podajemy ``guest``.

Po zalogowaniu się widzimy 3 pliki

.. code-block:: console

   fd@ubuntu:~$ ls -l
   total 16
   -r-sr-x--- 1 fd_pwn fd   7322 Jun 11  2014 fd
   -rw-r--r-- 1 root   root  418 Jun 11  2014 fd.c
   -r--r----- 1 fd_pwn root   50 Jun 11  2014 flag

flaga znajduje się w pliku ``flag``, natomiast nie mamy do niego dostępu.
Mamy natomiast możliwość wykonania programu ``fd``, który ma ustawiony ``suid`` pozwalający na odczyt flagi.

Uruchomienie aplikacji daje następujące wyjście:

.. code-block:: console

   fd@ubuntu:~$ ./fd
   pass argv[1] a number

Dlatego sprawdźmy co robi ta aplikacja.
Kod programu znajduje się w pliku ``fd.c``

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

Patrząc na kod, widzimy w liniach 6-8, że aplikacja wymaga co najmniej jednego argumentu.

Następnie, w linii 10 widzimy tworzenie zmiennej ``fd`` będącą wyliczeniem naszego argumentu, zrzutowanego do typu ``int``, a następnie pomniejszonego o wartość heksadecymalną ``0x1234``.

W linii 12 widzimy, że wyliczona wartość ``fd`` jest używana jako wartość ``file descriptor`` przy odczycie danych, które następnie zostają zapisane do zmiennej ``buf``.

Ostatecznie w linii 13, sprawdzane jest, czy wczytany bufor równy jest stringowi ``LETMEWIN``.

Ponieważ domyślnie podczas uruchamiania aplikacji otwierane są trzy deskryptory plików:

- ``0``: standardowe wejście
- ``1``: standardowe wyjście
- ``2``: standardowe wyjście błędów

najprościej będzie użyć istniejącego standardowego wejścia, czyli klawiatury do wczytania bufora.

Aby otrzymać ``0`` w zmiennej ``fd``, musimy jako argument przekazać wartość ``0x1234`` w zapisie dziesiętnym.

Sposobem którego ja używam do przeliczania takich wartości, jest użycie ``pythona``


.. code-block:: console

   fd@ubuntu:~$ python
   Python 2.7.12 (default, Nov 12 2018, 14:36:49) 
   [GCC 5.4.0 20160609] on linux2
   Type "help", "copyright", "credits" or "license" for more information.
   >>> 0x1234
   4660

Następnie wystarczy uruchomić program ``fd`` z argumentem ``4660`` oraz wpisać oczekiwaną frazę ``LETMEWIN``.

.. code-block:: console

   fd@ubuntu:~$ ./fd 4660
   LETMEWIN
   good job :)
   mommy! I think I know what a file descriptor is!!

I otrzymaliśmy flagę.

.. _pwnable: https://pwnable.kr
