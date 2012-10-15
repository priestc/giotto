.. _ref-introduction:

============
Introduction
============
Giotto is a full featured application framework inspired by the **Model, View, Controller** concept.
Its purpose is to enforce a style that separate the model and view,
so front end development and back end development are more closely linked.

Rationale
---------
Often times in web development shops, the development process is split up into two teams, **back-end** and **front-end**.
This occurs because front-end tasks are carried out by template designers,
who are not specialized in back end technologies such as databases and messaging queues.
A pain point in this separation is that front end developers work in isolation to back-end developers,
and miscommunication results.
For instance, front-end developers, in redesigning the HTML of a web project,
may add a new feature that (unbeknown to that front end dev),
requires significant back-end re-engineering.

Philosophy
----------
1. Giotto allows application developers to create application that can be written with all other web frameworks.
2. Giotto **does** force users to do things the "Giotto way". In other words, **convention over configuration**

Multiple Pluggable Controllers
------------------------------
One design aim of Giotto is to easily plug in controllers to a project
without having to make modifications to the model or view.

For instance, you can create a blog application that has both a complete web interface,
as well as a complete command line interface.

The advantage of this design is that back-end developers can write the model using the command line interface,
while the front-end developers build the HTML.
This optimizes the development process by making it easier to determine if a bug is coming from the model,
or if it is a result of the view.