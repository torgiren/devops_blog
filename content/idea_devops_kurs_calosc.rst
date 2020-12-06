Kurs DevOps
###########

:keywords: linux, kernel, hacking, devops
:tags: linux, kernel, hacking, devops
:status: draft
:slug: devops-course
:date: 2020-07-25

Zarys:

- Tworzenie maszyn w różnych serwisach
- Podstawy poruszania się po konsoli
- Podstawy vim
- Pierwsza strona hello world w html i uruchomienie jej w httpd
- Dodanie php
- postawienie wordpress
- postawienie dwóch wordpressów na różnych portach
- vhosty i różne adresy
- Przyjrzenie się protokołowi HTTP przez telnet
- Prosta baza danych mysql
- Prosta baza danych postgresql
- Haproxy jako balancer
- Blog postawiony na pelicanie
- ansible do stawiania bloga na pelicanie
- buildbot do CICD dla bloga
- Instalacja dockera deploy bloga jako kontener
- Deploy wordpressa jako kontener (być może ansiblem i buildbotem)
- Podstawy jenkinsa
- Podstawy iptables i filtrowania ruchu
- ssh config i proste opcje do proxyjumpów, przeierowania portów itp
- Podstawy C i prosta aplikacja sieciowa, która odczytuje też dysk
- podstawy strace - porównanie syscalli i opowiadających funkcji. iptables, mysql, timeout
- Apache tomcat i pierwsza aplikacja
- java i aplikacja w springboot
- Web Hello world w python, bottle, flask, django. uwsgi
- Bash, awk, perl do przeszukiwania logów
- Centralny serwer logów opraty o sysloga
- Named i dns. także SRV
- Postfix i null mailer
- przyjrzenie się protokołowi SMTP i telnet
- Konfiguracja używalnego serwera pocztowego - spf, dkim, greylist, skrzynki wirtualne
- service discovery. consul, etcd, zookeeper, eureka
- dynamiczny load balancer: haproxy? envoy?
- ldap, openid, ??? - freeipa, openldap, port389, dex, ???
- python i autoryzacja z powyższym
- go i autoryzacja z powyższym?
- php i autoryzacja z powyższym
- shared storage: nfs, gluster, ceph
- podstawy selinux. dodawanie portów, ustawiani kontaktów na plikach
- (wielka niewiadoma) własne reguły dla selinux
- ssl krok po kroku - czyli napisanie własnego clienta https.
- iac z użyciem terraforma
- monitoring usług i serwerów. nagios, shinken(??), icinga, prometheus, grafana
- rysowanie grafów infrastruktury - plantuml
- kontrola wersji - git
- hostowanie gia - github, gitolite, gitlab
- code review - gerrit, github, gitlab
- Job runner - rundeck
- systemy ticketowe - redmine, github
- wyrażenia regularne
- redis. czym jest, zastosowanie, klastrowanie
- rabbitmq. czym jest zastosownie, klastrowanie
- kafka. czym jest zastosowanie, klastrowanie
- postgresl. klastrowanie
- mariaDB. klastrowanie (??? wielki znak zapytania)
- openvpn
- cache http. nginx, varnish, cloudflare, ???
- uruchamianie aplikacji w chroot
- udostępnianie funkcjonalności poprzez authorized_keys i command
- Apache tomcat, multiinstancje
- budowanie pakietów rpm oraz własne repozytorium yum
- analiza struktury systemów plików ext4 (??? nie wiem czy to tutaj pasuje, czy nie lepiej na zwykly odcinek)
- protokół ssh, własny prosty klient ssh



Podstawy poruszania się po konsoli
==================================

Zacząć należy od wyjaśnienia czym jest konsola Linuksowa.
Jest to urządzenie pozwalające na komunikację z systemem operacyjnym.
Jednak najczęściej określenia "konsola" używa się jako skrót myślowy do emulatora terminala z uruchomioną powłoką.
I takie też znaczenie będzie nas interesowało w tym rozdziale.

Gdy logujemy się na serwer, zwykle używamy jakiegoś terminala z klientem ssh (dla systemów Windows może to być np putty).
Natomiast po zalogowaniu się, domyślnie zostaje uruchomiony program powłoki systemowej.

Powłoka daje możliwość komunikacji z systemem operacyjnym poprzez możliwość uruchamiania aplikacji.
Można by tutaj również napisać, że powłoka pozwala na wyświetlanie oraz edycję plików, ale tak na prawdę jest to uruchamianie małym programów wykonujących te czynności.
Dla przykładu: chcąc wypisać pliki w katalogu w którym się znajdujemy, używamy polecenia ``ls``, które jest małą aplikacją stworzoną tylko do wypisywania plików.
Dlatego określenie, że powłoka służy do uruchamiania innych programów uważam za trafne i wyczerpujące.

Większość powłok dostarcza również kilka wewnętrznych instrukcji pozwalających na pisanie skryptów o których opowiem w dalszej części rozdziału.

Zaczynając od początku.
Po zalogowaniu się, zobaczymy wyjście podobne do poniższego:

.. code-block:: console

   [vagrant@localhost ~]$

Jest to tak zwany "znak zachęty". Jest on konfigurowalny oraz może się różnić między różnymi systemami, ale przeważnie przyjmuje powyższą formę.
Widzimy tutaj trzy ważne informacje:

- ``vagrant`` - jest to nazwa użytkownika, który używa tej powłoki (tutaj będzie Twój login)
- ``localhost`` - jest to nazwa maszyny na której się znajdujemy
- ``~`` - jest to aktualny katalog w którym się znajdujemy. Może to być lekko mylące, ponieważ ``~`` jest specjalnym oznaczeniem katalogu domowego.

Warto tutaj zaznaczyć, że powyższy znak zachęty, jest znakiem zachęty powłoki ``bash``.
Istnieje wiele różnych powłok, lecz wszystkie służą do tego samego - komunikacji z systemem.
Aktualnie powłoka ``bash`` jest najczęstszą domyślną powłoką, dlatego też skupię się na niej.

Pierwszą rzeczą którą możemy chcieć zrobić, jest wypisanie miejsca w którym się znajdujemy.
Służy do tego polecenie (program) ``pwd``, którego pełna nazwa to ``print working directory``.

.. code-block:: console

   [vagrant@localhost ~]$ pwd
   /home/vagrant

Widzimy, że nasz aktualny katalog to ``/home/vagrant``.
Jak należy rozumieć powyższy zapis?
Większość systemów plików ma strukturę hierarchiczną, co w luźnym tłumaczeniu oznacza, że pliki mogą być zagnieżdżone w katalogach i podkatalogach.
W reprezentacji wizualnej, katalogi oddzielane są znakiem slash (/).
Dodatkowo, ważną informacją jest, że lokalizacja każdego pliku bądź katalogu zaczyna się od katalogu głównego, czyli ``/``.
Dlatego nasza ścieżka ``/home/vagrant`` może zostać przeczytana jako: "W katalogu głównym, znajduje się katalog ``home``, natomiast w tym katalogu znajduje się kolejny katalog ``vagrant`` i w tym właśnie katalogu aktualnie jesteśmy".

Kolejną rzeczą którą możemy chcieć zrobić, to zmienić aktualny katalog.
Ponieważ nie wiemy jeszcze jakie są katalogi w systemie, możemy chcieć przejść do katalogu głównego ``/``.
Aby to zrobić, użyjemy polecenia powłoki służącego do zmiany katalogu, czyli ``cd`` - co oznacza, ``change directory``.

.. code-block:: console

   [vagrant@localhost ~]$ cd /
   [vagrant@localhost /]$ pwd
   /

Widzimy, że po zmianie katalogu, znak zachęty uległ zmianie. Dotychczasowy znak ``~`` został zamieniony na ``/``, ponieważ naszym aktualnym katalogiem jest ``/``.
Co potwierdza również wypisanie aktualnego katalogu.

Naturalnym kolejnym krokiem, który możemy chcieć wykonać, że wypisanie plików oraz katalogów.
Aby to wykonać, użyjemy polecenia ``ls`` co pochodzi od ``list directory contents``.

.. code-block:: console

   [vagrant@localhost /]$ ls
   bin   dev  home  lib64  mnt  proc  run   srv       sys  usr      var
   boot  etc  lib   media  opt  root  sbin  swapfile  tmp  vagrant

Na większości terminali powyższe elementy mogą posiadać różne kolory, które oznaczają różne typy elementów.
Wśród katalogów, które znajdują się w katalogu głównym, widzimy katalog ``home``, który był katalogiem nadrzędnym dla naszego domowego. Wejdźmy do niego i wylistujmy pliki w nim.

.. code-block:: console

   [vagrant@localhost /]$ cd home
   [vagrant@localhost home]$ ls
   vagrant

Po zmianie katalogu na ``home``, ponownie widzimy zmianę znaku zachęty, wylistowanie plików w tymże katalogu, widzimy, że znajduje się tam jedynie nasz katalog ``vagrant`
