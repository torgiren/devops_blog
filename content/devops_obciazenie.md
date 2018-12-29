Title: Podstawowa analiza obciążenia systemu
Status: draft
keywords: linux, hacking, load, cpu, io
Summary: W tym artykule opisuję narzędzia i metody analizy różnych typów obciążenia.
Authors: TORGiren

W tym poście omówię różne typy obciążeń z jakimi możemy się spotkać podczas pracy z systemami GNU/Linux oraz przedstawię narzędzia, które są w stanie pomóc w analizie przyczyn tych obciążeń

Pojęcia podstawowe
------------------

### Co może być obciążone?

Najczęściej obciążonymi zasobami są `CPU` lub `IO`.
Obciążenie `IO` wpływa na `CPU`, dlatego w dalszej części będę omawiał tylko `CPU`.

Trzeba jednak pamiętać, że *obciążenie obciążeniu nierówne*.
Obciążenie `CPU` można podzielić na obciążenie wynikające z:

* prawidłowej pracy aplikacji
* błędu aplikacji powodujące wpadnięcie w pętlę nieskończoną
* użycia pamięci `SWAP`
* nieoptymalnego używania wywołań systemowych
* problemów z działaniem pamięci masowej
* TODO

### Statystyki używane przy analizie obciążenia

1) W [manualu](http://man7.org/linux/man-pages/man5/proc.5.html){:target="blank"} dotyczącym *pseudo-filesystemu* `proc` możemy znaleźć opis pliku `/proc/stat`.
  Opisane jest w nim kilka statystyk użycia `CPU`, które pomagają znaleźć przyczynę obciążenia systemu.
  Wartościami, które są najczęściej wykorzystywane przy analizie obciążenia są:

  * *user* - mówi ona o użyciu procesora przez kod uruchomionych aplikacji.
  * *nice* - j.w. lecz dla aplikacji uruchomionych z niskim priorytetem.
  * *system* - czas spędzany na wykonywaniu kodu jądra.
  * *idle* - czas bezczynności procesora.
  * *iowait* - czas jaki procesor spędza na oczekiwaniu na urządzenia wejścia/wyjścia.
  * *steal* - czas jaki system czeka na wirtualny `CPU` od systemu gospodarza w środowiskach wirtualnych.

2) W powyższym manualu znajduje się również opis pliku `/proc/meminfo`, który opisuje aktualne użycie pamięci.
   Najważniejsze znajdujące się w nim wartości (z punktu podstawowej analizy obciążenia) to:

  * *MemTotal* - opisuje rozmiar dostępnej w systemie pamięci `RAM`.
  * *MemFree* - ilość wolnej i nieużywanej pamięci.
  * *MemAvailable* - ilość dostępnej pamięci.
  * *SwapTotal* - rozmiar pamięci `SWAP`.
  * *SwapFree* - ilość wolnej pamięci `SWAP`.
  * *Dirty* - ilość bajtów w pamięci oczekujących na zapisanie na dysk.

3) TODO: Ruch sieciowy. Powinno wychodzić w sy i io, ale muszę to sprawdzić w domu na kompie.

### Narzędzia używane do analizy

Podczas analizy obciążenia systemu, najczęściej stosuje się następujące narzędzia:

* *top* - podstawowe narzędzie do monitorowania stanu systemu.
* *free* - wyświetla aktualne zużycie pamięci.
* *vmstat* - wyświetla stan pamięci oraz `CPU`.
* *strace* - monitoruje wywołania systemowe wykonywane przez aplikację.

Studium przypadków
------------------

### Wymagająca aplikacja działająca prawidłowo
Często zdarza się, że obciążenie `CPU` jest wysokie.
Głównie wyróżnia się wtedy statystyka `user`.
Oznacza to, że cały czas procesora spędzany jest na uruchomionej aplikacji.
Jeżeli w takim przypadku aplikacja odpowiada użytkownikowi oraz zapisuje *logi* w specyficznych dla siebie interwałach czasowych, możemy uznać, że aplikacja działa poprawnie tylko jest mocno obciążona.
Warto w takim przypadku rozważyć utworzenie bądź powiększenie klastra aplikacji w celu odciążenia maszyny.

### 100% CPU czyli aplikacja w pętli nieskończonej
Innym częstym przypadkiem jest błąd aplikacji powodujący wejście w różne typy pętli nieskończonych.
Objawia się to zwykle użyciem `user` na 100% dla jednego lub wielu rdzeni.
Zwykle aplikacja nie odpowiada wtedy na żądania użytkownika jak również nie zapisuje nic w swoich logach.
W przypadku aplikacji *Javowych*, często przed takich stanem można zauważyć w logach wyjątek `Out of memory`.

Ponieważ czasami aplikacje w tym stanie utylizują jedynie jeden rdzeń procesora, monitorowanie średniego obciążenia daje nieprawdziwe wyniki.
Weźmy dla przykładu maszynę posiadającą cztery rdzenie.
Gdy jedna z aplikacji ulegnie awarii i zużyje 100% `user` jednego rdzenia, średnie obciążenie `CPU` będzie na poziomie 25%, co przez wiele systemów monitoringu jest uznawane za wartość poprawną.

Jedną z metod analizy czy aplikacja wpadła w powyższy stan jest użycie polecenia `strace`.
Pozwala ono na *podglądanie* wywołań systemowych wykonywanych przez aplikację.
Jeżeli aplikacja nie wykonuje żadnych *rozsądnych* wywołań systemowych, tj. `open`, `read`, `write`, `connect`, 'accept', `clone` itp, a jedynie *syscall*-e z rodziny `futex`, bądź żadnych *syscall*-i, można przypuszczać, że wpadła w pętle nieskończoną.
Oczywiście, trzeba pamiętać, ze istnieje możliwość, iż aplikacja w danej chwili działa poprawnie, tylko otrzymała bardzo obciążające zapytanie.
Tutaj należy wspomóc się wiedzą dot. konkretnej aplikacji.

W przypadku gdy aplikacja nie przyjmuje nowych zapytań, a aktualnie przetwarzane (bądź pętla nieskończona) trwa dłużej niż wartość *timeout* przez którą aplikacja kliencka będzie oczekiwała na odpowiedź, dobrym rozwiązaniem jest restart aplikacji.

### *Swapowanie* czyli brak `RAM`-u
Również bardzo częstym, ale i zwykle łatwym do rozwiązania problemem jest brak pamięci `RAM` oraz *swapowanie* aplikacji.

Sytuacja taka objawia się zwykle poprzez trzy objawy.

* zwiększone czasy odpowiedzi aplikacji.
* zwiększony `load average` - od niskich rzędu dwukrotności ilości rdzeni, aż po wartości rzędu 700 czy 1500.
* wysoka wartość `iowait`.

Aby zweryfikować, czy taka sytuacja ma miejsce, warto wykonać dwa kroki.
Po pierwsze, używając polecenia `free` (polecam używanie flagi `-m` która wyświetla wartości w megabajtach a nie kilobajtach).
Jeżeli wyjście z polecenia `free` pokazuje nam, że wartość `used` jest zbliżona do wartości `total` oraz że mamy włączony `swap` oraz że `swap` jest w używany (kilka megabajtów jest akceptowalne) to może świadczyć o tym, że system był zmuszony część pamięci zapisać na dysk.  
Warto wtedy użyć narzędzia `top`, w celu sprawdzenia aktualnego użycia `CPU` i jego wartości `wa` (od `iowait`) oraz czy na liście procesów znaczącą ilość `CPU` używa proces `kswap`. Są to objawy małej ilość pamięci `ram`

W takim przypadku należy, jeśli do możliwe, dołożyć dodatkowej pamięci (co w środowiskach wirtualnych nie jest dużym problemem), bądź w przypadku posiadania kilku aplikacji na jednej maszynie rozważenie uruchomienie tych aplikacji na dedykowanych maszynach.

### *IO wait* czyli problemy z dyskiem
Tutaj sytuacja jest bardzo zbliżona do problemów ze `SWAP`.
Gdy aplikacja próbuje wykorzystywać urządzenia wejścia wyjścia w sposób bardziej wymagający niż pozwalają na to możliwości urządzeń, procesor spędza czas na zapisywaniu.
Rośnie wtedy obciążenie `io wait` oraz bardzo często `load` systemu.

W celu diagnostyki obciążenia dysku można użyć dwóch narzędzi:

* *iostat*
* *iotop*

*iostat* monitoruje utylizację dysków w systemie.
Po uruchomieniu polecenia `iostat` otrzymamy statystyki *od uruchomienia systemu*.
Aby włączyć tryb monitorowania ciągłego, należy podać jako parametr liczbę sekund co ile ma nastąpić odświeżenie.
Dodatkowo, przydatną opcją jest opcja `-x` która włącza wypisywanie bardziej szczegółowych statystyk.
Osobiście zawsze uruchamiam *iostat* poleceniem `iostat -x 1`.

Najważniejsze elementy które są prezentowane przez *iostat* to:

* `avg-cpu` które pokazuje aktualne obciążenie procesora
* `rkB/s` oraz `wkB/s` które pokazują ilość danych odczytywanych i zapisywanych na dane urządzenie
* `r_await` oraz `w_await` które pokazują czas w milisekundach jaki dane czekają na zapisanie
* `util` które pokazuje procent utylizacji danego urządzenia

W przypadku obserwacji, że któreś urządzenie ma podwyższone `util` należy ocenić, czy ilość danych zapisywany bądź odczytywanych jest zbyt duża (co może być sugestią to sklastrowania aplikacji w celu jej odciążenia), czy, w przypadku wysokiej utylizacji przy niskich transferach, mamy do czynienia z awarią dysku.

*iotop* jest narzędziem pozwalającym na identyfikację procesów najbardziej wykorzystujących zasoby dyskowe.
W przypadku, gdy *iostat* daje sugestię, że dyski twarde są sprawne oraz występuje duże ich obciążenie, *iotop* jest w stanie zidentyfikować który proces bądź procesy za to odpowiedzialne.
Aplikacja wypisuje uruchomione w systemie procesy oraz sortuje je ze względu na poziom w jakim wykorzystują dyski twarde.
Dodatkowo wypisuje ilość danych jakie dany proces odczytuje i zapisuje.  
Po ustaleniu najbardziej obciążającego procesu możemy przystąpić do analizy, czy takie zachowanie jest zachowaniem pożądanym.

### Wysokie *system cpu* czyli nieoptymalna aplikacja
TODO
