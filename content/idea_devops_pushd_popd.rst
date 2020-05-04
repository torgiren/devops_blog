Pushd/Popd
######################################

:keywords: linux, devops, bash, stack
:tags: linux, devops, bash, stack
:status: draft
:slug: pushd
:date: 2020-04-18

W tym poście pokażę jak działają bashowe polecenia ``pushd`` oraz ``popd``.

Powłoka ``bash`` posiada pewną funkcjonalność, która nie jest powszechnie znana - tą funkcjonalnością jest stos katalogów.

Jak sama nazwa wskazuje, jest to stos na którym odkładane są ścieżki do katalogów, a na jego szczycie znajduje się aktualny katalog.

Zanim przejdziemy do zastosowań, poznajmy trzy polecenia służące do obsługi tego stosu:

- ``pushd`` - służy do dodawania katalogu na stos
- ``popd`` - służy do zdejmowania katalogu ze stosu
- ``dirs`` - służy do wypisywania aktualnego stanu stosu

Sposobu działania każdego z powyższych poleceń będziemy uczyć się na przykładach :)

Na początku wypiszmy sobie aktualny stan stosu:

.. code-block:: console

   torgiren@redraptor ~ $ dirs -v
    0  ~
   torgiren@redraptor ~ $ cd /tmp
   torgiren@redraptor /tmp $ dirs -v
    0  /tmp

Widzimy, że polecenie ``dirs -v`` wypisuje aktualny stan stosu, który domyślnie zwiera tylko jedną pozycję - aktualny katalog

Następnie dodajmy jakiś katalog na wierzch stosu:

.. code-block:: console

   torgiren@redraptor /tmp $ pushd /proc/
   /proc /tmp
   torgiren@redraptor /proc $ dirs -v
    0  /proc
    1  /tmp

Widzimy, że katalog ``/proc`` został dodany na wierzch stosu, natomiast ``/tmp`` znajduje się na drugiej pozycji.
Widzimy również, że aktualny katalog zmienił się na ``/proc``.
Jak wspomniałem wcześniej, aktualny katalog to ten który znajduje się na wierzchu stosu, dlatego dodając ``/proc`` zmieniliśmy również aktualny katalog

Po zmianie katalogu metodą tradycyjną, czyli ``cd``, zauważamy, że:

.. code-block:: console

   torgiren@redraptor /proc $ cd /sys
   torgiren@redraptor /sys $ dirs -v
    0  /sys
    1  /tmp

najwyższy element uległ zmianie.

Następnie, spróbujmy zdjąć ze stosu najwyższy element:

.. code-block:: console

   torgiren@redraptor /sys $ popd
   /tmp
   torgiren@redraptor /tmp $ dirs -v
    0  /tmp

co tu się stało...

Polecenie ``popd`` zdjęło ze stosu najwyższy element, dlatego nowym najwyższym elementem stał się katalog ``/tmp`` co poskutkowało zmianą bieżącego katalogu właśnie na ``/tmp``

Z tą wiedzą, możemy przejść do przykładu z życia (jedno z dwóch najczęściej używanych przeze mnie zastosowań)

.. code-block:: console

   torgiren@redraptor /tmp $ pushd .
   /tmp /tmp
   torgiren@redraptor /tmp $ dirs -v
    0  /tmp
    1  /tmp
   torgiren@redraptor /tmp $ cd /etc
   torgiren@redraptor /etc $ cd conf.d
   torgiren@redraptor /etc/conf.d $ pwd
   /etc/conf.d
   torgiren@redraptor /etc/conf.d $ cd ..
   torgiren@redraptor /etc $ cd init.d/
   torgiren@redraptor /etc/init.d $ popd
   /tmp
   torgiren@redraptor /tmp $ dirs -v
    0  /tmp

co tu się dzieje...

Będąc w katalogu ``/tmp``, odkładam na stos bieżący katalog - czyli ``/tmp``.
Skutkuje to powstaniem dwóch wpisów ``/tmp`` na stosie.
Następnie zmieniam katalogi na ``/etc``, ``/etc/conf.d``, ``/etc/init.d``.
Jak wiemy, operacja ``cd`` zmienia tylko najwyższy element, dlatego na pozycji 1 wciąż znajduje się ``/tmp``.
Po skończonej pracy w katalogach ``/etc``, po wpisaniu ``popd`` ściągam aktualny katalog i pozycja 1 staje się pozycją 0, czyli wracamy do katalogu ``/tmp``.
Jest to ulepszona wersja ``cd -``, gdyż ``cd -`` pozwala wrócić tylko do poprzedniego katalogu, natomiast użycie stosu pozwala na dokonanie dowolnej liczby przejść pomiędzy katalogami a następnie powrót do zapamiętanej pozycji.

Polecenie ``pushd`` posiada również możliwość odkładania katalogów na stos bez zmiany aktualnego katalogu.
Są one wtedy odkładane na pozycję 1.

.. code-block:: console

   torgiren@redraptor /tmp $ cd /tmp/
   torgiren@redraptor /tmp $ mkdir -p pushd/a1
   torgiren@redraptor /tmp $ mkdir -p pushd/a2
   torgiren@redraptor /tmp $ mkdir -p pushd/a3
   torgiren@redraptor /tmp $ cd pushd/
   torgiren@redraptor /tmp/pushd $ touch a1/test.txt
   torgiren@redraptor /tmp/pushd $ touch a1/test2.txt
   torgiren@redraptor /tmp/pushd $ touch a1/test3.txt
   torgiren@redraptor /tmp/pushd $ pushd -n a1
   /tmp/pushd a1
   torgiren@redraptor /tmp/pushd $ pushd -n a2
   /tmp/pushd a2 a1
   torgiren@redraptor /tmp/pushd $ pushd -n a3
   /tmp/pushd a3 a2 a1
   torgiren@redraptor /tmp/pushd $ dirs -v
    0  /tmp/pushd
    1  a3
    2  a2
    3  a1

Z tak przygotowanym stosem, możemy przejść do drugiej najczęściej wykorzystywanego przeze mnie możliwości jaką daje stos katalogów.
Powiedzmy, że chcemy przenieść plik ``test2.txt`` do katalogu ``a2``, natomiast ``test3.txt`` do katalogu ``a3``. Zamiast robić standardowe ``mv a1/test2.txt a2``, możemy zrobić:

.. code-block:: console

   torgiren@redraptor /tmp/pushd $ mv ~3/test2.txt ~2/ -iv
   przemianowany 'a1/test2.txt' -> 'a2/test2.txt'
   torgiren@redraptor /tmp/pushd $ mv ~3/test3.txt ~1/ -iv
   przemianowany 'a1/test3.txt' -> 'a3/test3.txt'


mimo, że nie wydaje się to dużo lepsze i wygodniejsze niż tradycyjny ``mv``, zobaczmy inny, bardziej życiowy przykład:

.. code-block:: console

   torgiren@redraptor /tmp/pushd $ dirs -v
    0  /tmp/pushd
   torgiren@redraptor /tmp/pushd $ pushd .
   /tmp/pushd /tmp/pushd
   torgiren@redraptor /tmp/pushd $ dirs -v
    0  /tmp/pushd
    1  /tmp/pushd
   torgiren@redraptor /tmp/pushd $ cd /etc/
   torgiren@redraptor /etc $ cd conf.d/
   torgiren@redraptor /etc/conf.d $ cd ..
   torgiren@redraptor /etc $ cd init.d/
   torgiren@redraptor /etc/init.d $ cp mdadm ~1/a3/ -iv
   'mdadm' -> '/tmp/pushd/a3/mdadm'
   torgiren@redraptor /etc/init.d $ dirs -v
    0  /etc/init.d
    1  /tmp/pushd
   torgiren@redraptor /etc/init.d $ popd
   /tmp/pushd
   torgiren@redraptor /tmp/pushd $ dirs -v
    0  /tmp/pushd

dlatego powyższy przykład uważam za przydatny?
Ponieważ, na żadnym etapie nie jest wymagane dokładne znane ścieżki ani źródła ani celu.
W przypadku celu, zapisujemy aktualny katalog, a w przypadku źródła możemy dowolnie przemieszczać się pomiędzy katalogami w poszukiwaniu żądanego pliku.
A następnie, w prosty sposób powrócić do pierwotnego katalogu roboczego.

Kolejną rzeczą którą możemy zrobić używając stosu katalogów, jest jego rotacja.

Pozwala ona na przechodzenie po katalogach na stosie bez usuwania ich ze stosu.
Kierunek oraz krok o jaki zostanie przesunięty stos, podaje się jako argument w formie ``+/-num`` zamiast katalogu.

.. code-block:: console

   torgiren@redraptor /tmp/pushd/a2 $ pushd -n /tmp/pushd/a3
   /tmp/pushd/a2 /tmp/pushd/a3
   torgiren@redraptor /tmp/pushd/a2 $ pushd -n /tmp/pushd/a2
   /tmp/pushd/a2 /tmp/pushd/a2 /tmp/pushd/a3
   torgiren@redraptor /tmp/pushd/a2 $ cd /tmp/pushd/a1/
   torgiren@redraptor /tmp/pushd/a1 $ dirs -v
    0  /tmp/pushd/a1
    1  /tmp/pushd/a2
    2  /tmp/pushd/a3
   torgiren@redraptor /tmp/pushd/a1 $ pwd
   /tmp/pushd/a1
   torgiren@redraptor /tmp/pushd/a1 $ pushd +1
   /tmp/pushd/a2 /tmp/pushd/a3 /tmp/pushd/a1
   torgiren@redraptor /tmp/pushd/a2 $ pwd
   /tmp/pushd/a2
   torgiren@redraptor /tmp/pushd/a2 $ pushd +1
   /tmp/pushd/a3 /tmp/pushd/a1 /tmp/pushd/a2
   torgiren@redraptor /tmp/pushd/a3 $ pwd
   /tmp/pushd/a3
   torgiren@redraptor /tmp/pushd/a3 $ pushd +1
   /tmp/pushd/a1 /tmp/pushd/a2 /tmp/pushd/a3

Przedostatnią rzeczą, jaką można zrobić ze stosem, to zdejmowanie z niego wybranych elementów.
Ponieważ ``popd`` pozwala zdjąć nie tylko najwyższy, ale również dowolny inny element.
Określenie, który element ma zostać usunięty jest podawane jako argument numeryczny poprzedzony znakiem ``+`` bądź ``-`` określający, czy liczymy elementy od wierzchu czy od spodu stosu.
Dla przykładu, usuńmy ze stosu elementy ``a5``, ``a15``, ``a20``, ``a1``, ``a19``.

.. code-block:: console

   torgiren@redraptor /tmp/pushd $ for i in $(seq 1 20); do pushd -n a$i; done
   /tmp/pushd a1
   /tmp/pushd a2 a1
   /tmp/pushd a3 a2 a1
   /tmp/pushd a4 a3 a2 a1
   /tmp/pushd a5 a4 a3 a2 a1
   /tmp/pushd a6 a5 a4 a3 a2 a1
   /tmp/pushd a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a12 a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a13 a12 a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a14 a13 a12 a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a15 a14 a13 a12 a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a16 a15 a14 a13 a12 a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a17 a16 a15 a14 a13 a12 a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a18 a17 a16 a15 a14 a13 a12 a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a19 a18 a17 a16 a15 a14 a13 a12 a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   /tmp/pushd a20 a19 a18 a17 a16 a15 a14 a13 a12 a11 a10 a9 a8 a7 a6 a5 a4 a3 a2 a1
   torgiren@redraptor /tmp/pushd $ dirs -v
    0  /tmp/pushd
    1  a20
    2  a19
    3  a18
    4  a17
    5  a16
    6  a15
    7  a14
    8  a13
    9  a12
   10  a11
   11  a10
   12  a9
   13  a8
   14  a7
   15  a6
   16  a5
   17  a4
   18  a3
   19  a2
   20  a1
   torgiren@redraptor /tmp/pushd $ popd -4 # a5
   /tmp/pushd a20 a19 a18 a17 a16 a15 a14 a13 a12 a11 a10 a9 a8 a7 a6 a4 a3 a2 a1
   torgiren@redraptor /tmp/pushd $ popd +6 # a15
   /tmp/pushd a20 a19 a18 a17 a16 a14 a13 a12 a11 a10 a9 a8 a7 a6 a4 a3 a2 a1
   torgiren@redraptor /tmp/pushd $ popd +1 # a20
   /tmp/pushd a19 a18 a17 a16 a14 a13 a12 a11 a10 a9 a8 a7 a6 a4 a3 a2 a1
   torgiren@redraptor /tmp/pushd $ popd -0 # a1
   /tmp/pushd a19 a18 a17 a16 a14 a13 a12 a11 a10 a9 a8 a7 a6 a4 a3 a2
   torgiren@redraptor /tmp/pushd $ popd +1 # a19
   /tmp/pushd a18 a17 a16 a14 a13 a12 a11 a10 a9 a8 a7 a6 a4 a3 a2


I ostatnia operacja która może być przydatna, czyli wyczyszczenie stosu, pozostawiając jedynie bieżący katalog.
Używa się do tego polecenia ``dirs -c``

.. code-block:: console

   torgiren@redraptor /tmp/pushd $ dirs -v
    0  /tmp/pushd
    1  a18
    2  a17
    3  a16
    4  a14
    5  a13
    6  a12
    7  a11
    8  a10
    9  a9
   10  a8
   11  a7
   12  a6
   13  a4
   14  a3
   15  a2
   torgiren@redraptor /tmp/pushd $ dirs -c
   torgiren@redraptor /tmp/pushd $ dirs -v
    0  /tmp/pushd



