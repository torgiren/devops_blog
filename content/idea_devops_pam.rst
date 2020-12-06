PAM - Pluggable Authentication Modules
######################################

:keywords: linux, kernel, pam, hacking, devops, security
:tags: linux, kernel, pam, hacking, devops, security
:status: draft
:slug: pam
:date: 2020-07-25


Notes:

https://www.freebsd.org/doc/en/articles/pam/pam-sample-appl.html

W tym poście omówię 
- czym jest pam
- account, auth, password, session
- pliki /etc/pam.d/
- include, required, optional, requisite
- kilka modułów
- logika przez success
- wlasna aplikacja używająca pam
- własny moduł PAM

TODO: Sprawdzić xlock i jego chkpwd i odwolywanie sie do shadow bez suid root


W tym poście omówię czym jest PAM oraz jak z niego korzystać.

Czym jest PAM
-------------

PAM, czyli Pluggable Authentication Modules jest zbiorem różnych bibliotek, które odpowiedzialne są za uwierzytelnianie użytkowników.
Już na początku warto zaznaczyć, że nie jest to usługa w postaci demona, a jedynie zbiór procedur (co okaże się ważne podczas pisania własnej aplikacji używającej PAM).

PAM może być używany, gdy nie chcemy implementować w aplikacji obsługi wielu różnych metod uwierzytelniania i możemy użyć tych oferowanych przez system operacyjny.
Dodatkowo, oddelegowanie tego mechanizmu to systemu zewnętrznego, pozwala na poszerzanie wachlarza dostępnych metod jak i ich logiki, bez potrzeby przebudowywania aplikacji.

Działanie PAM
-------------

PAM udostępnia cztery interface-y które mogą być wykorzystywane podczas uwierzytelniania.

- `account` -  w tym kroku sprawdzana jest poprawność konta które ma zostać użyte do logowania
- `auth` - w tym kroku sprawdzana jest poprawność danych uwierzytelniających (hasło, klucz itp)
- `password` - w tym kroku sprawdzane jest hasło pod kątem wymogów bezpieczeństwa.
- `session` - w tym kroku podejmowane są czynności potrzebne do pełnego uruchomienia sesji (np: montowanie katalogów)

Konfiguracja PAM
----------------

PAM jest konfigurowany poprzez pliki w katalogu `/etc/pam.d` (istnieje również opcja konfiguracji przez `/etc/pam.conf`, ale używanie `/etc/pam.d` jest bardziej elastyczne)
J
Konfiguracje usług, które korzystają z PAM znjdują się w plikach o nazwach odpowiadających nazwom tych usług (np. `sshd`, `sudo`)

W każdym pliku znajdują się jednolinijkowe reguły, które mają następującą składnie:

.. code:

   type control module-path module-arguments

gdzie:

- `type` - określa czy reguła należy go grupy `auth`, `account`, `password` czy `session`
- `control` - określa zachowanie danej reguły. Mamy tutaj cztery standardowe metody

  - `required` - każda reguła określona jako `required` musi zakończyć się sukcesem. W przypadku niepowodzenia, kolejne reguły są wykonywane (co nie ma już wpływu na negatywny proces uwierzytelniania) w celu uniemożliwienia atakującemu detekcji etapu w którym wystąpiło niepowodzenie.
  - `requisite` - podobnie jak `required`. Różni się tylko sposobem zachowania w przypadku niepowodzenia. Po kroku który zwrócił negatywny wynik, następuje natychmiastowe przerwanie procesu uwierzytelniania (bądź aktualnego łańcucha jeśli takowy był użyty)
  - `sufficient` - jest to metoda mówiąca o tym, że jeżeli wszystkie poprzednie reguły `required` zakończyły się powodzeniem oraz reguła `sufficient` również zwróci wynik pozytywny, to aktualny łańcuch zostaje zakończony sukcesem bez wykonywania dalszych reguł w łańcuchu. W przypadku niepowodzenia, wynik jest ignorowany.
  - `optional` - wyniki reguł tego typu są ignorowane (chyba, że jest to jedyna reguła w łańcuchu). Zwykle używana, gdy chcemy zrobić jakieś dodatkowe operacje, które nie zawsze muszą się udać.

  Oprócz wspomnianych czterech podstawowych metod, istnieją dwie metody kontrolujące przepływ:

  - `include` - wstawia do aktualnego łańcucha reguły określone w innym pliku (wstawiane są tylko reguły tego samego typu co reguła wywołująca `include`)
  - `substack` - działa podobnie jak `include`, z tą różnicą, że tworzy nowy podłańuch. Wynik działanie reguł w łańcuchu interpretowany jest jako wynik reguły `substack` a nie całego łańcucha wywołującego (np. `sufficient` w podlancuchu zakończy przetwarzanie tylko danego podłańcucha)

  Ostatnią formą definicji metod zachowania jest definicja złożona. Przyjmuje ona formę `[value1=action1 value2=action2 ...]`.
  Pełną listę możliwych wartości można znaleźć w dokumentacji, jednak najważniejszymi są:

  - `success` - oznaczający, że uwierzytelnianie przy użyciu tego modułu zakończyło się sukcesem
  - `default` - określający domyślną akcję dla wartości które nie zostały zdefiniowane

  Natomiast akcja może być jedną z poniższych:

  - `ignore` - oznacza, że ten moduł powinien zostać zignorowany
  - `bad` - oznacza, że wynik działania modułu należy traktować jako niepowodzenie, ale przetwarzać kolejne reguły
  - `die` - podobnie jak `bad`, jednak natychmiastowo zaprzestaje przetwarzania aktualnego łańcucha. (różnica jak `required` i `requisite`)
  - `ok` - oznacza, że wynik działania modułu jest pozytywny
  - `done` - podobnie jak `ok`, z tą różnicą, że łańcuch nie jest dalej przetwarzany (podobnie jak `required` i `sufficient`)
  - `reset` - powoduje wyczyszczenie aktualnego stanu łańcucha i przetwarzanie kolejnych reguł (TODO: Sprawdzić empirycznie)
  - `<num>` - wartość numeryczna oznacza liczbę reguł które zostaną pominięte (używane przy konstruowaniu alternatywnych ścieżek uwierzytelniania)

  Jak widać, standardowe metody są jedynie skróconymi wersjami zapisu złożonego i mają następujące formy

  - `required` - `[success=ok new_authtok_reqd=ok ignore=ignore default=bad]`
  - `requisite` - `[success=ok new_authtok_reqd=ok ignore=ignore default=die]`
  - `sufficient` - `[success=done new_authtok_reqd=done default=ignore]`
  - `optional` - `[success=ok new_authtok_reqd=ok default=ignore]`

- `module-path` - określa ścieżkę do modułu który ma zostać użyty. Zwykle jest to ścieżka względna względem domyślnego katalogu z modułami pam (zależna od systemu), jednak może być również podana jako ścieżka bezwzględna

- `module-argument` - określa parametry przekazywane do używanego modułu. Jest to pole opcjonalne, gdyż nie każdy moduł jest parametryzowany. 

Przykładowe moduły
------------------

Przyjrzyjmy się kilku domyślnym modułom które można znaleźć w systemie

- `pam_unix.so` - najbardziej podstawowy moduł w systemie GNU/Linux. Zapewnia on interface dla wszystkich czterech typów reguł (account, auth, password, session). Pozwala on na uwierzytelnianie użytkowników w oparciu o pliki `/etc/passwd` oraz `/etc/shadow`.
- `pam_deny.so` - jak sama nazwa wskazuje, jest to moduł, który zawsze zwraca odmowę uwierzytelniania. Może być używny w każdym z czterech komponentów. Uzwykle używany na końcu łańcuchów, których logika zakłada, że wcześniejsze reguły posiadają pola `control` typu `sufficient` bądź odpowiednie formy złożone.
- `pam_permit.so` - jest to dokładne przeciwieństwo modułu `pam_deny.so`. Używany zwykle gdy nie potrzeba jest któregoś typu uwierzytelniania, badź podczas tworzenia rozdnieżdzonych konstrukcji warunkowych.
- `pam_succeed_if.so`
- `pam_listfile.so`
