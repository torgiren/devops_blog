Jak to jest z tym little-endian
###############################

:keywords: linux, hacking, little-endian, memory
:tags: linux, hacking, little-endian, memory
:date: 2019-07-29
:Status: draft
:slug: little-endian
:lang: pl

W tym poście postaram się opowiedzieć trochę o kolejności bitów w pamięci.

Zacznijmy od trzęsienia ziemi
-----------------------------

.. code-block:: C

    int main()
    {
        long int x=0x4142434445464748;
    }

.. code-block:: console

   $ gcc -g main.c -o main
   $ gdb main
   (gdb)$ break main
   (gdb)$ layout src
   (gdb)$ r
   (gdb)$ s

Na systemie 64-bitowym, nasza zmienna ma 8 bajtów.

Dlatego ją wypiszmy:

.. code-block:: console

  (gdb)$ x/1gx &x
  0x7fffffffdca8: 0x4142434445464748

ale 64 bity, to również 2x32 bit

.. code-block:: console

  (gdb)$ x/2wx &x
  0x7fffffffdca8: 0x45464748	0x41424344

ale to także, 4x16 bit

.. code-block:: console

  (gdb)$ x/4hx &x
  0x7fffffffdca8: 0x4748  0x4546  0x4344  0x4142

ale również 8x8 bit

.. code-block:: console

  (gdb)$ x/8bx &x
  0x7fffffffdca8: 0x48    0x47    0x46    0x45    0x44    0x43    0x42    0x41

Co jest nie tak z kolejnością?

a teraz niech napięcie rośnie...
--------------------------------

Aby to zrozumieć, należy wiedzieć, jak system zapisuje dane w pamięci.

Istnieją dwa sposoby przechowywania danych: ``big endiang`` oraz ``little endian``.

Zapis ``big endian`` charakteryzuje się tym, ze kolejność zapisu bitów jest analogiczna do tego jak my zapisujemy, czyli najbardziej znaczący bit jest zapisywany jako pierwszy, a najmniej znaczący, jako ostatni.  
W konwencji ``little endian`` jest natomiast odwrotnie. Najmniej znaczący bit jest zapisywany jako pierwszy, a najbardziej znaczący jako ostatni.

``Bit endian`` używany jest m.in w procesorach SPARC bądź PowerPC, jednak w większości powszechnie używanych procesorów króluje ``little endian``.
Dlatego dzisiaj się mu przyjrzymy bliżej.

Od początku? Od końca? Czy na przemian?
---------------------------------------

Jeśli spojrzymy na wyniki wypisania wartości z ``gdb``, zauważymy, że wypisując całą liczbę na raz, otrzymamy ją w takiej formie w jakiej zapisaliśmy.
Natomiast wypisując po bajcie, otrzymamy zapis od końca.
Ale dlaczego czy wypisywaniu po słowie bądź pół słowie mamy przemieszane bajty?

Całość łatwo zrozumieć gdy zapiszemy liczbę bitowo.

Liczba ``0x4142434445464748`` zapisana bitowo, ma wartość

  ``0100000101000010010000110100010001000101010001100100011101001000``

ponieważ, w konwencji ``little-endian`` bit najważniejszy jest na końcu, zapiszmy tą wartość od tył:

  ``0001001011100010011000101010001000100010110000100100001010000010``

tak ta liczba będzie przechowywana w pamięci.

To dlaczego raz widzimy ją poprawnie, raz mieszanie a raz od tył?

Dla prostoty podzielmy sobie tą liczbę wizualnie na bajty

  ``00010010 11100010 01100010 10100010 00100010 11000010 01000010 10000010``

Gdy odczytujemy liczbę, jako jedna dużą 64 bitową wartość, komputer wie jak ją odczytać i dostajemy oczekiwaną wartość.

Natomiast, gdy odczytujemy 2x32 bity, komputer oczyta pierwsze 32 bity, zinterpretuje i wypisze, a następnie zrobi to samo z kolejnymi. Wygląda to mniej więcej tak:


  ``(00010010 11100010 01100010 10100010) (00100010 11000010 01000010 10000010)``

Każda z tych dwóch liczb jest interpretowana osobo, dlatego dla każdej z nich kompilator odwraca kolejność bitów:

  ``(01000101 01000110 01000111 01001000) (01000001 01000010 01000011 01000100)``

a następnie wyświetla podane liczby. W powyższym przypadku będzie to:

  ``(0x45464748) (0x41424344)``

czyli wynik jaki otrzymaliśmy w gdb.

Podobna sytuacja występuje, gdy chcemy odczytać 4x16 bit

  ``(00010010 11100010) (01100010 10100010) (00100010 11000010) (01000010 10000010)``

po odwróceniu:

  ``(01000111 01001000) (01000101 01000110) (01000011 01000100) (01000001 01000010)``

i w zapisie heksadecymalnym:

  ``(0x4748) (0x4546) (0x4344) (0x4142)``

i ostatni krok dla formalności - przy zapisie po jednym bajcie

  ``(00010010) (11100010) (01100010) (10100010) (00100010) (11000010) (01000010) (10000010)``
 
odwrócenie:

  ``(01001000) (01000111) (01000110) (01000101) (01000100) (01000011) (01000010) (01000001)``

i interpretacja:

  ``(0x48) (0x47) (0x46) (0x45) (0x44) (0x43) (0x42) (0x41)``

