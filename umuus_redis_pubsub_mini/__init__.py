#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Jun Makii <junmakii@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""Utilities, tools, and scripts for Python.

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

"""
import sys
import json
import inspect
import uuid
import types
import os
import redis
import attr
import functools
import toolz
import addict
import fire
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=(__name__ == '__main__' and 'DEBUG' or
           os.environ.get(__name__.upper().replace('.', '__') + '_LOG_LEVEL')
           or os.environ.get('LOGGING_LOG_LEVEL') or 'DEBUG'),
    stream=sys.stdout)
logger.setLevel(
    __name__ == '__main__' and 'DEBUG'
    or os.environ.get(__name__.upper().replace('.', '__') + '_LOG_LEVEL')
    or os.environ.get('LOGGING_MODULE_LOG_LEVEL') or 'WARNING')
import umuus_logging_decorator
__version__ = '0.1'
__url__ = 'https://github.com/junmakii/umuus-redis-pubsub-mini'
__author__ = 'Jun Makii'
__author_email__ = 'junmakii@gmail.com'
__author_username__ = 'junmakii'
__keywords__ = []
__license__ = 'GPLv3'
__scripts__ = []
__install_requires__ = [
    'attrs>=18.2.0',
    'addict>=2.2.0',
    'redis>=3.0.1',
    'toolz>=0.9.0',
    'loguru>=0.2.1',
    'fire>=0.1.3',
    'umuus-logging-decorator@git+https://github.com/junmakii/umuus-logging-decorator.git#egg=umuus_logging_decorator-1.0',
]
__dependency_links__ = []
__classifiers__ = []
__entry_points__ = {
    'console_scripts':
    ['umuus_redis_pubsub_mini = umuus_redis_pubsub_mini:main'],
    'gui_scripts': [],
}
__project_urls__ = {}
__setup_requires__ = []
__test_suite__ = ''
__tests_require__ = []
__extras_require__ = {}
__package_data__ = {}
__python_requires__ = ''
__include_package_data__ = True
__zip_safe__ = True
__static_files__ = {}
__extra_options__ = {}
__download_url__ = ''
__all__ = []


@attr.s()
class Listener(object):
    callback = attr.ib()
    channel = attr.ib(None)
    redis_instance = attr.ib(None)
    return_exception = attr.ib(True)
    disable_on_completed = attr.ib(False)

    def __attrs_post_init__(self):
        self.channel = self.channel or ((hasattr(self.callback, '__module__')
                                         and self.callback.__module__ + '.'
                                         or '') + self.callback.__qualname__)
        self.spec = inspect.getfullargspec(self.callback)

    def get_wrapper(self):
        @functools.wraps(self.callback)
        def wrapper(*args, **kwargs):
            try:
                result = self.callback(*args, **kwargs)
                if not self.disable_on_completed:
                    self.on_completed(id=str(uuid.uuid4()), result=result)
                return result
            except Exception as err:
                self.on_error(err, id=str(uuid.uuid4()))

        return wrapper

    def normalizer(self, message):
        name, event, id = message['channel'].split(':', 2)
        data = json.loads(message['data'])
        return addict.Dict(locals())

    def serializer(self, result):
        return json.dumps((isinstance(result, dict) and result
                           or dict(data=result)))

    @umuus_logging_decorator.logger.decorator(level='ERROR')
    def on_error(self, err, id):
        self.redis_instance.instance.publish(
            self.channel + ':on_error:' + id,
            self.serializer(dict(error=str(err))))

    @umuus_logging_decorator.logger.decorator(level='INFO')
    def on_completed(self, id, result, **kwargs):
        self.redis_instance.instance.publish(
            self.channel + ':on_completed:' + id, self.serializer(result))

    @umuus_logging_decorator.logger.decorator(level='INFO')
    def on_next(self, message):
        try:
            data = self.normalizer(message)
            result = self.callback(
                **{
                    key: value
                    for key, value in data.data.items()
                    if self.spec.varkw or key in self.spec.args
                })
            if not self.disable_on_completed:
                self.on_completed(id=data.id, result=result)
        except Exception as err:
            self.on_error(err, id=data.id)
            return err

    def as_handler(self):
        return {
            self.channel + ':on_next:*': self.on_next,
        }


@attr.s()
class Redis(object):
    env = attr.ib(__name__.upper())
    options = attr.ib({})
    instance = attr.ib(None)
    listeners = attr.ib(attr.Factory(list))
    thread = attr.ib(None)

    def __attrs_post_init__(self):
        self.options = json.load(open(os.environ.get(self.env)))
        self.instance = redis.Redis(decode_responses=True, **self.options)

    @toolz.curry
    def subscribe(self, callback, channel=None, **kwargs):
        listener = Listener(
            callback=callback, channel=channel, redis_instance=self, **kwargs)
        self.listeners += [listener]
        return listener.get_wrapper()

    def run(self, **kwargs):
        self.pubsub = self.instance.pubsub()
        for listener in self.listeners:
            handler = listener.as_handler()
            logger.info(listener.channel)
            self.pubsub.psubscribe(**handler)
        self.thread = self.pubsub.run_in_thread(sleep_time=0.1, **kwargs)


instance = Redis()


def from_modules(modules):
    fns = [
        attr for module_name in modules
        for module in [__import__(module_name)]
        for key, attr in vars(module).items()
        if isinstance(attr, types.FunctionType) and not key.startswith('_')
    ]
    list(map(instance.subscribe, fns))
    instance.run()


def from_paths(paths):
    fns = [
        function for path in paths
        for module_name, function_name in [path.split(':')]
        for module in [__import__(module_name)]
        for function in [getattr(module, function_name)]
    ]
    list(map(instance.subscribe, fns))
    instance.run()


def run(options={}, **kwargs):
    options = addict.Dict(options, **kwargs)
    if options.modules:
        from_modules(options.modules)
    if options.module:
        from_modules([options.module])
    elif options.paths:
        from_paths(options.paths)
    elif options.path:
        from_paths([options.path])


def main(argv=None):
    fire.Fire()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
