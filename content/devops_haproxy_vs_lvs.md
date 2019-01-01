Title: Haproxy vs LVS
keywords: haproxy, lvs, linux, load, balancing
tags: youtube, haproxy, lvs
Summary: Omówienie zasady działania balancerów Haproxy i LVS oraz porównanie wydajności obydwu w środowisku z wysyconym łączem wychodzącym.
date: 2018-12-29
Status: published

W tym poście omówię temat balansowania ruchu. Przedstawię dwa popularne rozwiązania: *Haproxy* oraz *LVS*, a następnie przeprowadzę testy wydajności obydwu rozwiązań w środowisku z wysyconym łączem wychodzącym.

    Uwaga: Ten post jest pisany po nagraniu materiału na YouTube.
    Dlatego zachowany został chaotyczny charakter tego materiału

Teoria
------

{% youtube  iSSAVJg7_Pw  320 180 %}

### Czym jest balansowanie ruchu?
Wyobraźmy sobie, że mamy klientów, którzy chcą odpytać o stronę www, np: strona.pl.
Gdybyśmy mieli tylko jeden serwer obsługujący tę stronę, klient zawsze pytałby o żądaną stronę właśnie ten serwer.

I tu pojawia się potrzeba balansowania ruchu.
Robi się to w dwóch celach:

* **HA** (High Availability) czyli **wysoka dostępność**
* **HP** (High Performance) czyli **wysoka wydajność**

W klastrze *HA* mamy kilka serwerów.
Gdy jeden z nich ulegnie awarii, wtedy kolejne zapytania będą kierowane na inne, sprawne maszyny.
W efekcie klient zawsze otrzyma odpowiedź na swoje zapytanie.

W klastrze *HP* również mamy kilka serwerów.
Gdy serwis ma wielu klientów, to istnieje pewna ilość zapytań, przy których jeden serwer nie ma wystarczających zasobów, aby przetwarzać zapytania bez opóźnień.
Dlatego w klastrze *HP* zapytania kierowane są równolegle na wiele serwerów, aby rozłożyć obciążenie i umożliwić wydajną pracę wszystkich maszyn.

Ten post będzie dotyczył klastrów *High Performance* pod kątem dostępnej przepustowości łącza.

### Jak wygląda zapytanie HTTP

Weźmy za przykład dowolny obrazek (np. kota).
Jest to dobry przykład dla dzisiejszego posta, ponieważ zapytanie o obrazek jest małe, a odpowiedź (obrazek) jest proporcjonalnie bardzo duży.

Zapytanie `HTTP` wygląda następująco:

    GET /kot.jpg HTTP/1.0

Czyli, wysyłając do serwera zapytanie `HTTP`, które ma kilkanaście bajtów, otrzymamy odpowiedź w postaci obrazka, który będzie miał rozmiar nawet kilkunastu megabajtów.

Warto to powtórzyć.
Przy ruchu `HTTP` zwykle zapytania od klientów są małe, a odpowiedzi są duże.

### Jak działa *Haproxy*

*Haproxy* jest *load balancer*-em *natującym*, czyli gdy zapytanie trafia od klienta do *Haproxy*, ten nawiązuje połączenie do jednego z serwerów *backend*-owych (algorytmów wyboru do którego serwera nastąpi połączenie jest kilka), wykonuje (często identyczne, a jeśli nie, to bardzo zbliżone do oryginalnego) zapytanie `HTTP`.
Po serwer *backend*-owy odpowiada do *Haproxy* a to ostatecznie wysyła odpowiedź do klienta.

W związku z tym, może nastąpić sytuacja, w której sumaryczna odpowiedź od serwerów *backend*-owych, a co za tym idzie ruch wychodzący z *Haproxy* do klientów będzie większy niż przepustowość łącza doprowadzonego do serwera.
Powoduje to opóźnienia w otrzymywaniu przez klientów odpowiedzi, nie wynikające z braku standardowych zasobów jakimi są `CPU` bądź `RAM`.
W tym przypadku dokładanie kolejnych maszyn do klastra nie tylko nie poprawi sytuacji, ale wręcz może ją jeszcze pogorszyć.

Jednakże, są sposoby aby ten problem rozwiązać

### Jak działa *LVS*

*LVS* ma kilka trybów pracy.
Ja się skupię na trybie **direct routing**.
*LVS* jest *balancer*-em warstwy czwartej, ponieważ słucha na `IP` + port, jednak w trybie *direct routing* mechanizm dystrybucji ruchu działa na warstwie drugiej modelu *OSI*.
Dodatkowo *LVS* działa w jądrze systemu, bez udziału aplikacji w *userspace* co również wpływa pozytywnie na wydajność.

W *LVS* mamy jednego *director*-a (może być ich więcej, ale to już temat tworzenia *HA* dla samego *LVS*), oraz serwery *backend*-owe, które w *LVS* noszą nazwę **real server**-ów.

Każda maszyna w klastrze *LVS* ma swój adres `IP`. Dodatkowo, na potrzebny balansowania ruchu, należy przydzielić dodatkowy, wirtualny adres `IP`.
Ważną rzeczą, która odróżnia *LVS* (w trybie *direct routing*) od innych *load balancer*-ów jest fakt, że przydzielony wirtualny adres `IP` należy ustawić nie tylko na serwerze rozdzielającym ruch - *directorze*, ale również na wszystkich pozostałych serwerach - *real server*-ach.

Po takim przypisaniu adresów `IP` do maszyn, otrzymamy konflikty adresacji.
Dlatego należy tak skonfigurować *real server*-y, aby nie rozgłaszały *arp*-ów z wirtualnym adresem.
Tylko *director* może odpowiedzieć na zapytanie *arp* o wirtualny adres *balancer*-a.

#### Jak *LVS* przekazuje pakiety do *real server*-ów

Załóżmy, że w naszym klastrze mamy następujące maszyny:

    director:
    ip: 10.0.0.1
    virtual ip: 10.0.0.2
    mac: 00:00:de:ad:be:ef

    real server1:
    ip: 10.0.0.5
    virtual ip: 10.0.0.2
    mac: 00:00:fe:ed:fa:ce

    real server2:
    ip: 10.0.0.6
    virtual ip: 10.0.0.2
    mac: 00:00:de:af:ba:be

Gdy do *director*-a trafia pakiet, który w ramce na ustawione następujące wartości:

    (...)
    source ip: 172.10.4.4
    dest ip: 10.0.0.2
    dest mac: 00:00:de:ad:be:ef
    (...)

*Director* jedyne co robi, to podmienia TYLKO `dest mac` na adres `MAC` jednego z *real server*-ów.
Tak zmieniony pakiet może wyglądać następująco:

    :::aa hl_lines="4"
    (...)
    source ip: 172.10.4.4
    dest ip: 10.0.0.2
    dest mac: 00:00:de:af:ba:be
    (...)

Taki pakiet (po adresie `MAC`) trafi do *real server1*.
Po otrzymaniu takiego pakiety przez *real server* oraz zweryfikowaniu, że docelowy adres `IP` jest również adresem *real server*-a (tym wirtualnym), serwer zaczyna go przetwarzać.

Po przetworzeniu zapytania, *real server* (w przeciwieństwie do *Haproxy*) nie wysyła odpowiedzi do *director*-a, a odpowiada do maszyny, która jest wpisana w polu `source ip`. Jest to adres klienta.
Dlatego, *real server* wysyła odpowiedź bezpośrednio do klienta.
W przypadku w którym każdy *real server* ma osobne łącze wychodzące, każdy z nich może wysyłać taką ilość danych na jaką pozwala jego łącze.
Dlatego `uplink` *director*-a nie jest już problemem, gdyż żadne dane nie wracają przez niego.

Konfiguracja
------------

{% youtube uryo9AGgTFY 320 180 %}

### Maszyny aplikacyjne

Pierwszym krokiem jest konfiguracja  maszyn aplikacyjnych (*backend*-owych).
Będziemy potrzebowali:

* `nginx` - który będzie naszym serwerem www
* `wget` - który będzie potrzebny do pobrania obrazka z internetu
* `arptables` - który będzie blokował rozgłaszanie *arp*ów

Na wszystkich maszynach aplikacyjnych wykonujemy następujące polecenie:

    # yum install nginx wget arptables

Następnie, ściągamy dowolny obraz z internetu.
W przykładzie zostało wybrane zdjęcie Dolomitów.
Ma ono 4MB, co pozwoli w łatwy sposób wysycić łącze.

    # cd /usr/share/nginx/html
    # wget http://www.junglebook.sk/panoramy/2010-Dolomity/01.1140674_1140681.jpg

Kolejnym krokiem jest uruchomienie `nginx`.

    # systemctl start nginx

Domyślnie, maszyny utworzone przez *Vagrant*-a posiadają wirtualne karty sieciowe, które byłoby ciężko wysycić.
Próbując wygenerował ruch mogący wykorzystać cały 1Gbps obciążenie `CPU` wzrosło by w znaczącym stopniu.
Dlatego, aby zasymulować wysycenie łącza ograniczmy przepustowość naszego *interface*-u do 10Mbps.
Do tego celu użyjemy *traffic control*.

    # tc qdisc add dev eth0 root tbf rate 10240kbit latency 50ms burst 1540

Następnie musimy skonfigurować wirtualny adres IP.
Jednak musimy zapewnić mechanizm blokujący rozgłaszanie *arp* dla tego adresu.
Do tego celu użyjemy `arptables`, któremu przekażemy parametr `-s` określający adres IP którego dotyczy reguła, `-j` określający docelowy łańcuch - w tym przypadku `DROP`, oraz `-A` określający łańcuch w którym ma się znaleźć reguła.

    # arptables -A OUTPUT -s 192.168.121.2 -j DROP

Mając już zabezpieczenie przed kolizją adresów, możemy dodać nasz wirtualny adres IP

    # ip addr add 192.168.121.2/32 dev lo

Wykorzystujemy tutaj maskę `/32` ponieważ ten adres nie ma żadnej sieci w którą się będzie komunikował oraz urządzenie `lo` wybrane jako losowy *interface* do którego przypniemy adres.

Przetestujmy czy konfiguracja serwerów aplikacyjnych jest poprawna.
W tym celu użyjemy narzędzia `apache benchmark`
Wykonując polecenie:

    # ab -n 100 -c 5 http://192.168.121.13/01.1140674_1140681.jpg
    (...)
    Failed requests: 0
    (...)
    Transfer rate: 1194.86 [Kbytes/sec] received
    (...)

dostaniemy w wyniku podsumowania informację, że żadne zapytanie nie zakończyło się błędem, co świadczy o tym, że serwer *www* został skonfigurowany poprawnie oraz informację, że średni transfer wynosił 1194 KBps, co w przeliczeniu na kilobity daje ok 9552 Kbps, co potwierdza, że ograniczenie przepustowości łącza również zostało skonfigurowane poprawnie.

### Maszyna balansująca ruch

#### Haproxy

W celu zainstalowania *haproxy* wykonujemy polecenie

    # yum install haproxy

Do naszych celów wykorzystamy domyślną konfigurację w której zmienimy adresy serwerów *backend*-owych na nasze oraz usuniemy `acl` dla plików statycznych.  
W pliku `/etc/haproxy/haproxy.cfg` zmieniamy sekcje `backend app` na:

    backend app
        balance roundrobin
        server app1 192.168.121.141 check
        server app2 192.168.121.13 check
        server app3 192.168.121.142 check
        server app4 192.168.121.28 check

oraz usuwamy z sekcji `frontend main *:5000` linijki dotyczące `acl`

    acl url_static *
    use_backend static *

i wykonujemy restart `haproxy`

    systemctl restart haproxy

#### LVS

W celu zainstalowania narzędzia do konfiguracji *LVS* wykonujemy polecenie

    # yum install ipvsadm

Następnie dodajemy adres wirtualny do balansera (należy zwrócić uwagę, że w tym przypadku nie ustawiamy reguł na *arptables*) do *interface*-u zewnętrznego.

    # ip addr add 192.168.121.2/24 dev eth0

Ostatnim krokiem jest skonfigurowanie samego *LVS*.
Wykonujemy to poprzez utworzenie *listener*-a który będzie słuchał na porcie 80.

    # ipvsadm -A -t 192.168.121.2:80

a następnie dodajemy *real server*-y.

    # ipvsadm -a -t 192.168.121.2:80 -r 192.168.121.141 -g
    # ipvsadm -a -t 192.168.121.2:80 -r 192.168.121.142 -g
    # ipvsadm -a -t 192.168.121.2:80 -r 192.168.121.13 -g
    # ipvsadm -a -t 192.168.121.2:80 -r 192.168.121.28 -g

Porównanie
----------

{% youtube 3z8Ilu8-vzY 320 180 %}

W celu porównania wydajności obu rozwiązań, zróbmy test polegający na pobraniu 100 obrazków z równoległą liczbą połączeń wynoszącą 12.

*Haproxy*:

    # ab -n 100 -c 12 http://192.168.121.29:5000/01.1140674_1140681.jpg
    (...)
    Time taken for tests: 388.511 seconds
    Transfer rate: 1180.92 [Kbytes/sec] received
    (...)

*LVS*:

    # ab -n 100 -c 12 http://192.168.121.2/01.1140674_1140681.jpg
    (...)
    Time taken for tests: 99.823 seconds
    Transfer rate: 4596.12 [Kbytes/sec] received
    (...)

Poniżej znajduje się wykres utylizacji łącza podczas testów.

[![Wykres transferu danych w Haproxy oraz LVS](/thumbs/devops_haproxy_vs_lvs_wykres_porownawczy_thumbnail_tall.jpg "Wykres transferu danych w Haproxy oraz LVS")]({static}/images/devops_haproxy_vs_lvs_wykres_porownawczy.jpg)

Jak widać na pierwszym wykresie, przy zapytaniach kierowanych do *Haproxy*, jeden z serwerów ma tzw. *sufit*, czyli ilość wysyłanych danych osiągnęła wartość maksymalną.
Ten charakterystyczny kształt wykresu pojawia się często, nie tylko w kontekście sieci, i zwykle oznacza, że mierzona wartość jest wąskim gardłem, gdyż jest wysycona w 100%.
Dodatkowo widzimy co pewien czas, duże *piki*.
Jest to transfer wchodzący.
Ponieważ na *traffic control* limitowaliśmy jedynie ruch wychodzący, to ruch wchodzący może być większy.
Taka właśnie sytuacja tutaj następuje.
Widzimy również, że cztery maszyny oscylują z ruchem wychodzącym w okolicach 5Mbps.
Wynika to z faktu, że nie limitujemy ruchu wchodzącego, dlatego serwery *backend*-owe mogą wysyłać sumarycznie powyżej 10Mbit.
Natomiast *Haproxy* może zwracać do klienta dane jedynie z szybkością 10Mbit, dlatego nadwyżka jest odbierana i przechowywana w *cache* na maszynie z *Haproxy*.
W przypadku, gdyby limit był ustawiony również na ruch wchodzący, powyższe piki by nie występowały, a ruch z maszyn aplikacyjnych byłyby sumarycznie równy 10Mbit i również byłby zbliżony do *sufitu*.  
Wartość odczytana z `apache benchmark` jest porównywalna z wartościami z wykresów (niedokładność wartości na wykresie wynika z niedokładności w konfiguracji).
Czyli, limit 10Mbit na maszynie widać zarówno jako *sufit* na wykresie, jak i `Transfer rate` w `apache benchmark`

W przypadku *LVS* sytuacja się diametralnie różna.
Widzimy, że wykres jest znacznie krótszy niż w przypadku *Haproxy*.
Dodatkowo ponownie widzimy efekt *sufitu*, jednak tym razem cztery serwery wysyłają z maksymalną możliwą prędkością.
Jeśli chodzi o ruch na maszynie balansującej, to widzimy niski sufit na poziomie ok 0.5Mbit, ponieważ przez *balancer* idą tylko małe zapytania *HTTP*.  
Zachowanie odczytane z wykresu ma swoje odzwierciedlenie w wynikach `apache benchmark`.

Widzimy, że w przypadku *LVS* zarówno `Tranfer rate` jest czterokrotnie większy, jak i sumaryczny czas testu jest czterokrotnie mniejszy.
To pokazuje, że w środowisku w którym następuje wysycenie łącza wychodzącego rozwiązaniem może być zastosowanie *LVS* w trybie *direct routing*.

Zachęcam do komentowania w odpowiednimi filmami na YouTube
