.. _debugging-with-gdb:

Debugging
=========

Desktop Mode
------------

The easiest way to do GDB Debugging via Clickable is desktop mode and can be started
by running ``clickable desktop --gdb``.

Alternatively a GDB Server can be started with ``clickable desktop --gdbserver <port>``
(just choose any port, e.g. ``3333``). Check for an option to do GDB Remote Debugging in your IDE
and connect to ``localhost:<port>``. To connect a GDB Client run
``gdb <app-binary> -ex 'target remote localhost:<port>'``.

To analyze errors in memory access run ``clickable desktop --valgrind``.

.. _on-device-debugging:

On Device
---------

Two terminals are required to do debugging on the device, one to start the ``gdbserver``
and the other one to start ``gdb``. In the first terminal run ``clickable gdbserver``
and in the second one ``clickable gdb``. This method is limited to
apps that are started via their own binary file.

The ``clickable gdbserver`` command provides the server at ``localhost:3333``. In theory
one could connect to that one from within any IDE. But to actually make it work, one needs
to provide the corresponding libc6 debug symbols. Otherwise the App won't start due to a
segfault.

For detailed instructions on how to use gdb check out `gdb documentation <https://sourceware.org/gdb/current/onlinedocs/gdb/>`__.
