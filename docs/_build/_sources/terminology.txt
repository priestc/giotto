.. _ref-terminology:

===========
Terminology
===========

* **Contrete Controller** - A file that launches a *controller process*.
  This file contains configuration information, such as hostname, port to listen to.
  The result of running the ``giotto_project`` utility is the creation of one or more concrete controller files.

* **Controller Class** - A type of controller, such as IRC, HTTP and CMD.
  Giotto ships with three controller classes: IRC, HTTP and CMD.

* **Controller Process** - A process that listens for user input, and invokes a giotto program when the user gives it data.