memsource-wrap
##############
Memosource API Wrap Library for Python


Ecamples
========

::

    import memsource

    m = memsource.Memsource('your user ame', 'your password')
    print(m.client.create('test client'))
    # will return id of the client
