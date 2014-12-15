.. image:: https://travis-ci.org/gengo/memsource-wrap.svg?branch=master
    :target: https://travis-ci.org/gengo/memsource-wrap

memsource-wrap
##############
Memsource API Wrap Library for Python


Examples
========

::

    import memsource

    m = memsource.Memsource(user_name='your user name', password='your password')
    print(m.client.create('test client'))
    # will return id of the client

If you already have token, you can omit user_name and password. In this case, this SDK can skip authentication, so it's bit faster.

::

    import memsource

    m = memsource.Memsource(token='your token')
    print(m.client.create('test client'))
    # will return id of the client
