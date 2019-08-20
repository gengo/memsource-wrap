.. image:: https://travis-ci.org/gengo/memsource-wrap.svg?branch=master
    :target: https://travis-ci.org/gengo/memsource-wrap

memsource-wrap
##############
Memsource API Wrap Library for Python

This library require Python 3.5. If Python 3.5 is not installed on your system, I recommened to use `Pythonz <https://github.com/saghul/pythonz>`_

Install
=======

::

    pip install -e 'git+https://github.com/gengo/memsource-wrap.git@master#egg=Package'

Uninstall
=========

::

    pip uninstall memsource-wrap

Examples
========

::

    import memsource.memsource

    m = memsource.memsource.Memsource(user_name='your user name', password='your password')
    print(m.client.create('test client'))
    # will return id of the client

If you already have token, you can omit user_name and password. In this case, this SDK can skip authentication, so it's bit faster.

::

    import memsource.memsource

    m = memsource.memsource.Memsource(token='your token')
    print(m.client.create('test client'))
    # will return id of the client
