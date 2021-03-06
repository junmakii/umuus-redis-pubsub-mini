
umuus-redis-pubsub-mini
=======================

Installation
------------

    $ pip install git+https://github.com/junmakii/umuus-redis-pubsub-mini.git

Example
-------

    $ umuus_redis_pubsub_mini

    >>> import umuus_redis_pubsub_mini

----

    $ export UMUUS_REDIS_PUBSUB_MINI=FILE.json

----

    @umuus_redis_pubsub_mini.instance.subscribe()
    def foo(x, y):
        return x * y

    @umuus_redis_pubsub_mini.instance.subscribe(channel='TEST')
    def bar(x, y):
        return x * y

    umuus_redis_pubsub_mini.instance.run()
    umuus_redis_pubsub_mini.instance.run(daemon=True)

----

    @umuus_redis_pubsub_mini.instance.subscribe(disable_on_completed=True)
    def bar(x, y):
        return x * y

----

    $ redis-cli --csv PSUBSCRIBE '*'

    $ redis-cli PUBLISH 'umuus_redis_pubsub_mini.fn:on_next:1' '{"x": 2, "y": 3}'

----

    $ python umuus_redis_pubsub_mini.py run --module my_module
    $ python umuus_redis_pubsub_mini.py run --path my_module.foo

----

With Class
----------

    class Foo:
        @classmethod
        @instance.subscribe()
        def test_classmethod(self, x, y=2):
            return x * y

        def test_method(self, x, y=2):
            return x * y

    instance.subscribe(Foo().test_method)

Authors
-------

- Jun Makii <junmakii@gmail.com>

License
-------

GPLv3 <https://www.gnu.org/licenses/>