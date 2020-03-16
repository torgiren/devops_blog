Common /dev/ devices
####################

:keywords: linux, dev, kernel
:tags: linux, dev, kernel
:date: 2019-12-15
:status: published
:slug: dev-devices

W tym poście przedstawię kilka urządzeń systemu GNU/Linux, których znajomość jest przydatna w pracy administratora systemu.

.. youtube:: 7H99VwPUb9s

Wstęp
-----

Wszystkie specjalne pliki urządzeń obsługiwane przez jądro są opisane w źródłach jądra w pliku `<https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/devices.txt/>`_.

Ja skupię się na tych, które uważam za najczęściej używane.

/dev/null
---------

Chyba jedno z najczęściej używanych urządzeń urządzeń jest ``/dev/null``. Jest to urządzenie które jest puste, a to znaczy, że przy próbie odczytu z niego, nie otrzymamy żadnych danych:

.. code:: console

  $ hexdump -C /dev/null 

natomiast zapisz powoduje porzucenie tych danych

.. code:: console

  $ echo "test" >/dev/null

Najczęstszym przypadkiem użycia tego urządzenia, jest zapis do niego danych, gdy nie chcemy ich otrzymać na ekran:

.. code:: console

  $ ps aux > /dev/null


/dev/zero
---------

Urządzenie ``/dev/zero``, jak sama nazwa wskazuje, zwraca zawsze zero.  Zwykle się z niego tylko odczytuje.
Zera są najczęściej używane przy tworzeniu plików, które chcemy aby były od razu zaalokowane (w przeciwieństwie do polecenia ``truncate``).

.. code:: console

  $ dd if=/dev/zero of=/tmp/file.dat bs=1k count=10k
  10240+0 records in
  10240+0 records out
  10485760 bytes (10 MB, 10 MiB) copied, 0.0252958 s, 415 MB/s


/dev/random oraz /dev/urandom
-----------------------------

Urządzenia ``/dev/random`` oraz ``/dev/urandom`` zwracają losowe dane ze specjalnej puli losowych danych w jądrze.
Różnią się one zachowaniem w przypadku wyczerpania puli losowych danych.  
W przypadku ``/dev/random``, odczyt zostaje zablokowany do czasu pojawienia się nowych danych, natomiast ``/dev/urandom`` generuje liczby pseudolosowe.  
Dlatego zwykle używane jest urządzenie ``/dev/urandom``, gdyż odczyt nigdy nie jest blokowany, natomiast ``/dev/random`` zalecane jest, gdy generowane dane muszą mieć duży współczynnik losowości i aby nie było możliwe przeprowadzenie ataku na generator liczb pseudolosowych.
Taką sytuacje mamy w przypadku generowania kluczy oraz innych danych związanych z bezpieczeństwem.

Aktualny stan wypełnienia puli danych losowych możemy sprawdzić w pliku ``/proc/sys/kernel/random/entropy_avail``

.. code:: console

  $ cat /proc/sys/kernel/random/entropy_avail
  4012

Dane z tych urządzeń możemy odczytywać jak z każdego innego pliku binarnego, np:

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

Często zdarza się, że jakaś aplikacja wymaga dużej ilość danych losowych z urządzenia ``/dev/random``, co powoduje powolne jej działanie.  
W takiej sytuacji możemy użyć aplikacji ``rngd``, która zasila pulę entropii danymi ze sprzętowego generatora liczb losowych (o ile takowy jest obecny)

/dev/full
---------

Ostatnim urządzeniem omawianym w tym poście, będzie ``/dev/full``.
Jest to chyba najmniej znane urządzane spośród dzisiaj omawianych.

Urządzenie przy próbie odczytu z niego nie zwraca żadnych danych.

Natomiast przy próbie zapisu, zwraca błąd ``ENOSPC``, czyli brak wolnego miejsca.
Jest to zwykle wykorzystywane przy testowaniu aplikacji pod kątem obsługi błędów związanych z zapisem na pełny wolumen.

.. code:: console

   $ dd if=/dev/random of=/dev/full bs=1k count=1
   dd: error writing '/dev/full': No space left on device
   0+1 records in
   0+0 records out
   0 bytes copied, 0.00015115 s, 0.0 kB/s


Bonus
-----

W przypadku przypadkowego usunięcia któregoś z urządzeń, można w łatwy sposób odtworzyć je korzystając z dokumentacji oraz polecenia ``mknod``.

Dla przykładu, usuńmy urządzenie ``/dev/urandom``

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

