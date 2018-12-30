Title: Haproxy vs LVS
keywords: haproxy, lvs, linux, load, balancing
tags: youtube, haproxy, lvs
Summary: Omówienie zasady działania balancerów Haproxy i LVS oraz porównanie wydajności obydwu w środowisku z wysyconym łączem wychodzącym.
date: 2018-12-29

W tym poście omówię ideę balansowania ruchy, przedstawię dwa popularne rozwiązania: *Haproxy* oraz *LVS*, a następnie przeprowadzę testy wydajności obydwu rozwiązań w środowisku z wysyconym łączem wychodzącym.

    Uwaga: Ten post jest pisany po nagraniu materiały na YouTube.
    Dlatego zachowany został chaotyczny charakter tego materiału

Teoria
------

#{% youtube  iSSAVJg7_Pw %}

### Czym jest balansowanie ruchu?
Wyobraźmy sobie, że mamy klientów, którzy chcą odpytać o stronę www, np: strona.pl.
Gdybyśmy mieli tylko jeden serwer obsługujący tą stronę, klient by zawsze pytał o żądaną stronę właśnie ten serwer.

I tu pojawia się potrzeba balansowania ruchu.
Robi się to w dwóch celach.

* **HA** (High Availability) czyli **wysoka dostępność**
* **HP** (High Performance) czyli **wysoka wydajność**

W klastrze *HA* mamy kilka serwerów.
Gdy jedna z nich ulegnie awarii, wtedy kolejne zapytania będą kierowane na inne, sprawne maszyny.
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
