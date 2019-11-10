=====
Python Library for Systemair Save VTR
=====

pysystemair_save_vtr is python wrapper for modbus communication with Systemair Save VTR units. The module uses modbus to communicate with the unit. It has only been tested with Systemair IAM module.

=====
Usage
=====

Package can be found on PyPI: https://test.pypi.org/project/pysystemair_save_vtr/

It can be installed using::

    pip install pysystemair_save_vtr

Package consists of SystemairSaveVTR module and can be used in following way::

    import pysystemair_save_vtr

    unit = SystemairSaveVTR(client, 1)
    unit.update()



===========================
Hardware compatibility list
===========================

The module has been testet with following hardware:

* Systemair SAVE VTR 300
* Systemair Internet Access Module (IAM) for modbus communication

If you test it with other units, please let me know or even better update the list above.

=============
Documentation
=============
