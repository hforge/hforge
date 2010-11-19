.. _git:

Introduction to ``git``
#######################

.. index:: git

.. contents::

.. highlight:: sh

If you want to get more involved in the development of :mod:`itools`, or just
to send patches from time to time, there are two things you need to know:

* The Coding Style [#git-coding-style]_.
* The usage of ``git``, and in particular the way it is used for
  :mod:`itools`.

Every software project, even the smallest one, will benefit from a *Control
Version System*, and ``git`` is probably the best.


Install ``git``
===============

For the instructions that follow in this chapter to work properly, you will
need a recent version of ``git``, 1.5 at least.

The latest version of ``git`` can be downloaded from their web site:

    http://git.or.cz

But if you use GNU/Linux, probably your distribution will include it.  For
example, to install ``git`` in a Gentoo [#git-gentoo]_ system type::

    $ sudo emerge dev-util/git

For Debian [#git-debian]_ or Ubuntu [#git-ubuntu]_ type::

    $ sudo apt-get install git-core git-doc git-email gitk


Configuration
=============

Once ``git`` is installed, you should configure it. The only thing required is
to give your full name and your email address::

    $ git config --global user.name "Luis Belmar-Letelier"
    $ git config --global user.email "luis@itaapy.com"

The parameters set with the command ``git config`` are written to the
configuration file :file:`.gitconfig`, in the user's home folder. It looks
like this:

.. code-block:: none

    [user]
    email = luis@itaapy.com
    name = Luis Belmar-Letelier


Configuration variables
-----------------------

There are, however, other configuration variables that most people would like
to define. Like for example to use colors::

    $ git config --global color.branch auto
    $ git config --global color.diff auto
    $ git config --global color.status auto

If you are going to send patches by email, you also should define the variable
``sendemail.smtpserver``::

    $ git config --global sendemail.smtpserver smtp.my-isp.com

For the complete list of configuration variables, check the ``git config``
manual page::

    $ git config --help


Environment variables
---------------------

The user's name and email address should be defined in the configuration file.
But sometimes it may be useful to override this information for a short period
of time; that can be done with some environment variables::

    $ export GIT_AUTHOR_NAME="Luis Belmar-Letelier"
    $ export GIT_COMMITTER_NAME="Luis Belmar-Letelier"
    $ export GIT_AUTHOR_EMAIL="luis@itaapy.com"


Check out :mod:`itools`
=======================

::

    $ cd ~/sandboxes
    $ git clone git://git.hforge.org/itools.git
    Initialized empty Git repository in /.../itools/.git/
    remote: Counting objects: 22399, done.
    remote: Compressing objects: 100% (6091/6091), done.
    ...
    $ cd itools
    $ git status
    # On branch master
    nothing to commit (working directory clean)

To see your local and remote branches use ``git branch``, without and with the
option ``-r`` respectively::

    # Local branches
    $ git branch
    * master

    # Remote branches
    $ git branch -r
    ...
    origin/0.15
    origin/0.16
    origin/0.20
    ...
    origin/HEAD
    origin/master

For now you only have one local branch called *master*, it is a branch of
*origin/master*. Later we will see how to create new branches.


How to keep your Branch up-to-date
==================================

The most basic thing you will want to do is to keep your branch up-to-date.
This is done through a two step process, where the first one is to fetch the
origin branches::

    $ git fetch origin
    ...
    Fetching refs/heads/0.15 from git://git.hforge.org/itools.git...
    Fetching refs/heads/0.16 from git://git.hforge.org/itools.git...
    Fetching refs/heads/0.20 from git://git.hforge.org/itools.git...
    ...

This command updates your copy of the origin branches.  Now you can ask what
is the difference between your local branch *master* and the origin master
branch::

    $ git log master..origin
    commit f4b64a9e49ed9ce66858ccd5461a0ef48a5870af
    Author: J. David Ibanez <jdavid@itaapy.com>
    Date:   Thu Apr 5 11:57:57 2007 +0200

        [xml] No more subclassing the Element class.


    commit 76698ec4bbea9f27447c2aee71c76af5a510efd9
    Author: J. David Ibanez <jdavid@itaapy.com>
    Date:   Wed Apr 4 19:26:13 2007 +0200

        [xhtml,html] Now XHTML and HTML elements are the same...

The output shows the new patches available (if your code is up-to-date the
output will be empty). To synchronise with the trunk, use ``git rebase``::

    $ git rebase origin
    First, rewinding head to replay your work on top of it...
    HEAD is now at f4b64a9... master
    Fast-forwarded master to origin.


How to create new Branches
==========================

Now imagine that you want to work not in the *master* branch, but in the
latest stable branch, *0.60* in this example. To do so you will have to create
a new local branch based on *0.60*, this is done with the command ``git
branch``::

    $ git branch 0.60 origin/0.60
    Branch 0.60 set up to track remote branch refs/remotes/origin/0.60.
    $ git branch
    0.60
    * master

To switch from one branch to another we use ``git checkout``::

    $ git checkout 0.60
    Switched to branch "0.60"
    $ git branch
    * 0.60
      master

As we have seen before to synchronize your *0.60* branch you will use ``git
fetch`` and ``git rebase``::

    # Fetch origin
    $ git fetch origin

    # Synchronize
    $ git checkout 0.60
    $ git rebase origin/0.60


How to make a Commit
====================

Now maybe you want to make some changes to :mod:`itools`. To use as an
example, we are going to make some really useless changes::

    # Edit an existing file
    $ vi __init__.py
    ...

    # Add a new file
    $ vi USELESS.txt
    ...

What have we done? Use ``git status`` to have an overview::

    $ git status
    # On branch 0.60
    # Changed but not updated:
    #   (use "git add <file>..." to update what will be committed)
    #
    #       modified:   __init__.py
    #
    # Untracked files:
    #   (use "git add <file>..." to include in what will be committed)
    #
    #       USELESS.txt
    no changes added to commit (use "git add" and/or "git commit -a")

One thing the excerpt above shows is how important it is to read the output of
the ``git`` commands, it will often tell *what to do next*.

Before committing it is a good idea to double check the changes we have done,
use ``git diff`` for this purpose::

    $ git diff
    diff --git a/USELESS.txt b/USELESS.txt
    new file mode 100644
    index 0000000..ddb4b9a
    --- /dev/null
    +++ b/USELESS.txt
    @@ -0,0 +1 @@
    +I was here!
    diff --git a/__init__.py b/__init__.py
    index 482b002..8a1ea48 100644
    --- a/__init__.py
    +++ b/__init__.py
    @@ -16,8 +16,14 @@
     # along with this program; if not, write to the Free Software
     # Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA...

    +"""
    +This is itools. Period.
    +"""
    +
    +
     # Import from itools
     from utils import get_version, get_abspath


    +# The version
     __version__ = get_version(globals())

Now you must tell ``git`` what changes you want to commit, for this we use the
``git add`` command::

    $ git add __init__.py
    $ git add USELESS.txt
    $ git status
    # On branch 0.60
    # Changes to be committed:
    #   (use "git reset HEAD <file>..." to unstage)
    #
    #       new file:   USELESS.txt
    #       modified:   __init__.py
    #

And now we can commit::

    $ git commit
    Created commit 612f41c: Add some useless comments.
     2 files changed, 7 insertions(+), 0 deletions(-)
     create mode 100644 USELESS.txt

The call to ``git commit`` will open your favourite text editor so you can add
a sensitive description for your commit.


Other commands
--------------

We have seen the use of ``git add`` to add a new file or to tell that an
existing file has been modified. There are other two commands you will need:

* ``git rm`` To remove a file.
* ``git mv`` To move or rename a file.


How to send a Patch
===================

To send your patches to be included in the main tree, the first step is always
to synchronize::

    $ git fetch origin
    $ git rebase origin/0.60
    ...

If there have been new patches in the origin branch that conflict with your
own patches, ``git rebase`` will fail, but it will give you instructions on
how to address the issue. Read these instructions carefully, solve the
conflicts and go ahead.

Now you can check the patches you have done with ``git log``::

    $ git log origin/0.60..0.60
    commit 612f41cd3aa3f9dce0f0f54a55e46971d29e5ee8
    Author: J. David Ibanez <jdavid@itaapy.com>
    Date:   Wed Jun 27 15:50:45 2007 +0200

        Add some useless comments.

Everything is alright? Time to build the patches, with ``git format-patch``::

    $ git format-patch origin/0.60
    0001-Add-some-useless-comments.patch

This call creates one file for every patch. Now you can send the patches.
There are two ways: upload to *bugzilla*, or send by email.


Upload to *bugzilla*
--------------------

If there is an open issue in *bugzilla* for the bug or enhancement your patch
addresses, it is best to attach the patch to that issue. If there is not, you
may want to open one. The following figure shows the *bugzilla*'s interface to
attach a patch.

.. figure:: figures/bugzilla_add_patch.*
    :align: center

    *Bugzilla*'s interface to attach a patch.


Send by email
-------------

To send a patch by email use the ``git send-email`` command::

    $ git send-email --to itools@hforge.org \
    > 0001-Add-some-useless-comments.patch

See the address to send the patches is the :mod:`itools` mailing list. You may
also send the patch directly to me jdavid@itaapy.com.


Summary of ``git`` commands
===========================

See below a summary of the ``git`` commands seen in this chapter::

    git add
    git branch
    git checkout
    git clone
    git commit
    git config
    git diff
    git fetch
    git format-patch
    git log
    git rebase
    git mv
    git rm
    git send-email
    git status


Help!
-----

For details about a command type::

    $ git <command> --help



.. rubric:: Footnotes

.. [#git-coding-style] Explained in another document, see :ref:`style`

.. [#git-gentoo] http://www.gentoo.org

.. [#git-debian] http://www.debian.org

.. [#git-ubuntu] http://www.ubuntu.com

