Chroot
######

:keywords: linux, chroot, hacking
:tags: linux, chroot, hacking
:date: 2018-12-29
:Status: draft

W tym poście omówię ręczne tworzenie *chroot*-a, uruchamianie w nim aplikacji a także wykorzystanie go wraz z usługą *ssh*, do ograniczania uprawnień użytkowników logujących się do serwera.

Czym jest *chroot*?
-------------------

*Chroot* jest skrótem od *change root* i określa mechanizm zmiany katalogu bazowego dla uruchamianego procesu.
Powoduje to, że dany proces oraz wszystkie jego procesy pochodne odnosząc się do ścieżki `/` odnoszą się do zmienionego katalogu.

Aktualny katalog *root* można sprawdzić w podsystemie *proc*.
Dla przykładu: proces *bash*, o *pid* 8429, został uruchomiony w *chroot*.
Jego katalog *root* widziany z systemu bazowego:

.. code-block:: console

   # ls -l /proc/8429/root
   lrwxrwxrwx. 1 root root 0 01-05 11:04 /proc/8429/root -> /tmp/ch

Natomiast sprawdzając ten sam atrybut z wewnątrz *chroot*-a, otrzymamy

.. code-block:: console

    # ls -l /proc/8429/root
    lrwxrwxrwx. 1 0 0 0 Jan  5 10:04 /proc/8429/root -> /

Wynika z tego, że proces uruchomiony w *chroot* nie ma wiedzy o tym, że jego *root* został zmieniony.

Jak zrobić pierwszego *chroot*-a?
---------------------------------

Wzorem solucji do gier ze starych pism komputerowych, poprowadzę Cię "za rączkę" i stworzymy minimalnego *chroot*-a.
Będę również pokazywał pojawiające się błędy, ponieważ ich występowanie w dużym stopniu wyjaśnia podejmowane kroki w celu stworzenia *chroot*-a.

Naszym pierwszym celem, będzie uruchomienie `bash` w *chroot*-cie.
W tym celu musimy utworzyć katalog w którym będzie nasz nowy *root*, a następnie wgrać do niego plik binarny `bash` (najlepiej do podkatalogu `bin`, dla zachowania wyglądu zwykłego *filesystem*-u.

.. code-block:: console

   $ mkdir /tmp/first_chroot
   $ mkdir /tmp/first_chroot/bin
   $ cp /bin/bash /tmp/first_chroot/bin/

Następnie spróbujmy uruchomić `bash`-a w *chroot*-cie.
Aby to zrobić, należy z użytkownika *root* wykonać polecenie `chroot`, a jako argumenty przekazać: katalog na który chcemy zmienic *root*-a oraz polecenie które chcemy uruchomić.

.. code-block:: console

    # chroot /tmp/first_chroot/ /bin/bash
    chroot: failed to run command ‘/bin/bash’: No such file or directory

Otrzymaliśmy błąd, że nie ma takiego pliku ani katalogu.
Jest to bardzo mylący błąd, ponieważ ten plik istnieje.

Dokładniej o tym problemie opowiem w innym odcinku.
Na tą chwilę musimy tylko wiedzieć, żę w nagłówkach *ELF* `bash`-a, mamy wpis dotyczący lokalizacji *INTERPRETER*-a, który ma zostać uruchomiony dla tej aplikacji

.. code-block:: console

   $ readelf -a /bin/bash|grep INTERP -A2
   INTERP         0x000154 0x00000154 0x00000154 0x00013 0x00013 R   0x1
       [Requesting program interpreter: /lib/ld-linux.so.2]

Jak widać, jako interpreter jest ustawiony linker.
Ponieważ w *chroot*-cie proces jako `/` bierze katalog *chroot*-owy, dlatego musimy również skopiować linker:

.. code-block:: console 

   $ mkdir /tmp/first_chroot/lib
   $ cp /lib/ld-linux.so.2 /tmp/first_chroot/lib/ -iv

W tej chwili możemy ponownie spróbować uruchomić `bash`-a w *chroot*-cie.

.. code-block:: console 

   # chroot /tmp/first_chroot/ /bin/bash
   /bin/bash: error while loading shared libraries: libtinfo.so.6: cannot open shared object file: No such file or directory

Powyższy błąd oznacza, że linker próbuje załadować biblioteki współdzielone i nie jest w stanie ich zlokalizować.
Dlatego trzeba je również dograć.
Trzeba pamiętać, że poszukiwany plik jest najczęściej *symlink*-iem do konkretnej wersji biblioteki:

.. code-block:: console 

   $ ls -l /lib/libtinfo.so.6
   lrwxrwxrwx. 1 root root 15 2018-05-09  /lib/libtinfo.so.6 -> libtinfo.so.6.1

Dlatego, gdy kopiujemy potrzebne biblioteki, należy przekopiować zarówno *symlink* jak i samą bibliotekę

.. code-block:: console 

   $ cp /lib/libtinfo.so.6 /lib/libtinfo.so.6.1 /tmp/first_chroot/lib -iv
   '/lib/libtinfo.so.6' -> '/tmp/first_chroot/lib/libtinfo.so.6'
   '/lib/libtinfo.so.6.1' -> '/tmp/first_chroot/lib/libtinfo.so.6.1'

Po przegraniu biblioteki, możemy ponownie spróbować przełączyć się do *chroot*

.. code-block:: console 

   # chroot /tmp/first_chroot/ /bin/bash
   /bin/bash: error while loading shared libraries: libdl.so.2: cannot open shared object file: No such file or directory

Widzimy, że teraz występuje problem z kolejną biblioteką.
Aby nie wgrywać po jednej bibliotece i sprawdzać jakiej jeszcze brakuje, odczytajmy wszystkie potrzebne biblioteki i wgrajmy je za jednym razem.
Aby odczytać potrzebne biblioteki, użyjemy polecenia `ldd`

.. code-block:: console 

   $ ldd /bin/bash
       linux-gate.so.1 (0xb7ede000)
       libtinfo.so.6 => /lib/libtinfo.so.6 (0xb7d5e000)
       libdl.so.2 => /lib/libdl.so.2 (0xb7d59000)
       libc.so.6 => /lib/libc.so.6 (0xb7bb5000)
       /lib/ld-linux.so.2 (0xb7ee0000)

Widzimy, że brakuje mam `libdl.so.2`, `libc.so.6`

.. code-block:: console 

   $ cp -iv /lib/libdl.so* /lib/libc.so* /tmp/first_chroot/lib/ 
   '/lib/libdl.so' -> '/tmp/first_chroot/lib/libdl.so'
   '/lib/libdl.so.2' -> '/tmp/first_chroot/lib/libdl.so.2'
   '/lib/libc.so' -> '/tmp/first_chroot/lib/libc.so'
   '/lib/libc.so.6' -> '/tmp/first_chroot/lib/libc.so.6'

Teraz, gdy mamy wszystkie potrzebne biblioteki, możemy w końcu uruchomić naszą powłokę w *chroot*

.. code-block:: console 

   # chroot /tmp/first_chroot/ /bin/bash
   bash-4.4#

Widzimy, że została uruchomiona powłoka `bash`.
Jednak, nie działają żadne podstawowe polecenia systemu Linux: `ls`, `mkdir`, `mount` itp.
Jest tak dlatego, że w naszym *chroot* mamy jedynie `bash`-a.
Działają natomiast polecenia samej powłowki: `cd`, `pwd` itp.

Poszerzmy teraz naszego *chroot*-a o polecenie `ls`

.. code-block:: console 

   $ cp -iv /bin/ls /tmp/first_chroot/bin/
   '/bin/ls' -> '/tmp/first_chroot/bin/ls'
   $ ldd /bin/ls
   linux-gate.so.1 (0xb7f75000)
   libselinux.so.1 => /lib/libselinux.so.1 (0xb7f04000)
   libcap.so.2 => /lib/libcap.so.2 (0xb7efe000)
   libc.so.6 => /lib/libc.so.6 (0xb7d5a000)
   libpcre2-8.so.0 => /lib/libpcre2-8.so.0 (0xb7cd3000)
   libdl.so.2 => /lib/libdl.so.2 (0xb7cce000)
   /lib/ld-linux.so.2 (0xb7f77000)
   libpthread.so.0 => /lib/libpthread.so.0 (0xb7caf000)
   $ cp -iv /lib/libselinux.so.1 /lib/libcap.so.2* /lib/libpcre2-8.so.0* /lib/libpthread.so* /tmp/first_chroot/lib/ 
   '/lib/libselinux.so.1' -> '/tmp/first_chroot/lib/libselinux.so.1'
   '/lib/libcap.so.2' -> '/tmp/first_chroot/lib/libcap.so.2'
   '/lib/libcap.so.2.25' -> '/tmp/first_chroot/lib/libcap.so.2.25'
   '/lib/libpcre2-8.so.0' -> '/tmp/first_chroot/lib/libpcre2-8.so.0'
   '/lib/libpcre2-8.so.0.7.0' -> '/tmp/first_chroot/lib/libpcre2-8.so.0.7.0'
   '/lib/libpcre.so.1.2.10' -> '/tmp/first_chroot/lib/libpcre.so.1.2.10'
   '/lib/libpthread.so' -> '/tmp/first_chroot/lib/libpthread.so'
   '/lib/libpthread.so.0' -> '/tmp/first_chroot/lib/libpthread.so.0'

gdy dogramy już aplikację `ls` oraz potrzebne biblioteki, możemy wykonać w naszym *chroot* polecenie `ls`.
Warto przed tym ustawić odpowiedni zmienna `PATH`, gdyż niekoniecznie będzie ona ustawiona na katalog `bin`

.. code-block:: console 

   # PATH=$PATH:/bin/
   # ls -l
   drwxrwxr-x. 2 1000 1000  80 Jan  5 13:52 bin
   drwxrwxr-x. 2 1000 1000 360 Jan  5 13:56 lib

Tak przygotowany *chroot* zapewnia nam izolację procesów w nim uruchomionych od pozostałego *filesystem*-u.

Uruchamianie aplikacji w *chroot*
---------------------------------

Jak przykładową aplikację, uruchomimy sobie wbudowany w *python*-a 3 server HTTP.
Aby to zrobić, wkopiujemy plik binarny, potrzebne biblioteki systemowe oraz wszystkie pliki interpretera *python* (wartym rozważenia rozwiązaniem jest również instalacja danej aplikacji w odpowiednich katalogach, zamiast kopiowanie plików)

.. code-block:: console

   $ cp /usr/bin/python3.6 /tmp/first_chroot/bin/
   $ ldd /tmp/first_chroot/bin/python3.6
           linux-gate.so.1 (0xb7f02000)
           libpython3.6m.so.1.0 => /lib/libpython3.6m.so.1.0 (0xb7b83000)
           libpthread.so.0 => /lib/libpthread.so.0 (0xb7b64000)
           libdl.so.2 => /lib/libdl.so.2 (0xb7b5f000)
           libutil.so.1 => /lib/libutil.so.1 (0xb7b5b000)
           libm.so.6 => /lib/libm.so.6 (0xb7a59000)
           libc.so.6 => /lib/libc.so.6 (0xb78b5000)
           /lib/ld-linux.so.2 (0xb7f04000)
   $ cp -iv /lib/libpython3.6m.so* /lib/libutil.so* /lib/libm.so* /tmp/first_chroot/lib/ -iv
   '/lib/libpython3.6m.so' -> '/tmp/first_chroot/lib/libpython3.6m.so'
   '/lib/libpython3.6m.so.1.0' -> '/tmp/first_chroot/lib/libpython3.6m.so.1.0'
   '/lib/libutil.so' -> '/tmp/first_chroot/lib/libutil.so'
   '/lib/libutil.so.1' -> '/tmp/first_chroot/lib/libutil.so.1'
   '/lib/libm.so' -> '/tmp/first_chroot/lib/libm.so'
   '/lib/libm.so.6' -> '/tmp/first_chroot/lib/libm.so.6'
   $ mkdir /tmp/first_chroot/usr/lib -p
   $ cp /usr/lib/python3.6 /tmp/first_chroot/usr/lib/
   $ cp -iv /lib/libz.so* /tmp/first_chroot/lib
   
Następnie możemy uruchomić naszą przykładową aplikację:

.. code-block:: console

   # /bin/python3.6 -m http.server 8998

Teraz możemy zobaczyć jaką korzyść niesie uruchomienie aplikacji w *chroot*.
Załóżmy, że *atakujący*, wykorzystując błędy w aplikacji, przejął nad nią kontrolę i jest w stanie odczytać dowolne pliki z dysku.
My na te potrzeby uruchomiliśmy serwer HTTP, który taką możliwość daje z założenia, ale efekt jest taki sam: klient łączący się do aplikacji ma dostęp do tych plików do których ma aplikacja.
Łącząc się pod adres `http://127.0.0.1:8898` widzimy, że aplikacja, a co za tym idzie atakujący ma dostęp jedynie do plików umieszczonych w *chroot*

.. code-block:: console

   $ curl http://127.0.0.1:8898
   <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
   <html>
   <head>
   <meta http-equiv="Content-Type" content="text/html; charset=ascii">
   <title>Directory listing for /</title>
   </head>
   <body>
   <h1>Directory listing for /</h1>
   <hr>
   <ul>
   <li><a href="bin/">bin/</a></li>
   <li><a href="lib/">lib/</a></li>
   <li><a href="tmp/">tmp/</a></li>
   <li><a href="usr/">usr/</a></li>
   </ul>
   <hr>
   </body>
   </html>

Oznacza to, że w przypadku kompromitacji jednej aplikacji, nie następuje kompromitacja pozostałych uruchomionych tam aplikacji jak również samego systemu.

Zamykanie zdalnych użytkowników w *chroot*
------------------------------------------

Częstą praktyką jest również zamykanie zdalnych użytkowników w *chroot*-ach.
Najłatwiej zrobić to poprzez utworzenie grupy użytkowników, a następnie dodawania kolejnych do tejże grupy.

.. code-block:: console

   $ groupadd chrooties
   $ useradd chroot1 -g chrooties -M
   $ passwd chroot1

Warto tutaj zwrócić uwagę na parametr `-M`, który mówi, aby `useradd` nie tworzył katalogu domowego - nie będzie nam on teraz potrzebny.
W sytuacji w której będziemy chcieli logować się po kluczu, może się on okazać przydatny.
Jednak w naszym przypadku zadowolimy się logowaniem hasłem.

Ważną rzeczą, którą trzeba tutaj zaznaczyć, są wymagania *ssh* co do uprawnień katalogu do którego będzie robiony *chroot*.
Z przyczyn bezpieczeństwa, *ssh* wymaga, aby cała ścieżka do katalogu była w rękach *root*-a i tylko *root*-a.
Dlatego musimy przenieść nasz `first_chroot` poza `tmp` oraz nadać mu odpowiednie uprawnienia.

.. code-block:: console

   $ mv /tmp/first_chroot/ /
   # chown root:root /first_chroot/
   # chmod 755 /first_chroot/


Teraz możemy skonfigurować *ssh*.
W pliku `/etc/ssh/sshd_config` musimy dopisać sekcję dotyczącą naszych użytkowników

.. code-block:: none

   Match Group chrooties
           ChrootDirectory /first_chroot

Po wykonaniu restartu, się zalogować i wylistować katalogi

.. code-block:: console

   $ ssh chroot1@localhost
   chroot1@localhost's password: 
   Last login: Sun Jan  6 08:25:41 2019 from 127.0.0.1
   -bash-4.4$ /bin/ls
   bin  lib  tmp  usr

Widzimy, że użytkownik został zamknięty w przygotowanym *chroot*.
Teraz już tylko w gestii administratora, co będzie posiadał w tym *chroot*.

Podsumowanie
------------

Pokazaliśmy sobie czym jest *chroot*, jak go utworzyć, jak uruchomić w nim aplikację oraz zamknąć *użyszkodników*.
Zachęcam do zadawania pytań oraz komentowania pod filmem na yt.
