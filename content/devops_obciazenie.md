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

### Aplikacja w pętli nieskończonej

