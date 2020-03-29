PAM - Pluggable Authentication Modules
######################################

:keywords: linux, kernel, pam, hacking, devops, security
:tags: linux, kernel, pam, hacking, devops, security
:status: draft
:sllug: pam

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

PAM udostępnia cztery interface-y które mogą być wykorzystywane podczas uwierzytelniania.

- `account` -  w tym kroku sprawdzana jest poprawność konta które ma zostać użyte do logowania (h
