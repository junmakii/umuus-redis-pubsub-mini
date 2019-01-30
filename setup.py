
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def run_tests(self):
        import sys
        import shlex
        import pytest
        errno = pytest.main(['--doctest-modules'])
        if errno != 0:
            raise Exception('An error occured during installution.')
        install.run(self)


setup(
    packages=setuptools.find_packages('.'),
    version='0.1',
    url='https://github.com/junmakii/umuus-redis-pubsub-mini',
    author='Jun Makii',
    author_email='junmakii@gmail.com',
    keywords=[],
    license='GPLv3',
    scripts=[],
    install_requires=['attrs>=18.2.0',
 'addict>=2.2.0',
 'redis>=3.0.1',
 'toolz>=0.9.0',
 'loguru>=0.2.1',
 'fire>=0.1.3'],
    dependency_links=[],
    classifiers=[],
    entry_points={'console_scripts': ['umuus_redis_pubsub_mini = umuus_redis_pubsub_mini:main'],
 'gui_scripts': []},
    project_urls={},
    setup_requires=[],
    test_suite='',
    tests_require=[],
    extras_require={},
    package_data={},
    python_requires='',
    include_package_data=True,
    zip_safe=True,
    download_url='',
    name='umuus-redis-pubsub-mini',
    description='Utilities, tools, and scripts for Python.',
    long_description=('Utilities, tools, and scripts for Python.\n'
 '\n'
 'umuus-redis-pubsub-mini\n'
 '=======================\n'
 '\n'
 'Installation\n'
 '------------\n'
 '\n'
 '    $ pip install '
 'git+https://github.com/junmakii/umuus-redis-pubsub-mini.git\n'
 '\n'
 'Example\n'
 '-------\n'
 '\n'
 '    $ umuus_redis_pubsub_mini\n'
 '\n'
 '    >>> import umuus_redis_pubsub_mini\n'
 '\n'
 '----\n'
 '\n'
 '    @umuus_redis_pubsub_mini.instance.subscribe()\n'
 '    def foo(x, y):\n'
 '        return x * y\n'
 '\n'
 "    @umuus_redis_pubsub_mini.instance.subscribe(channel='TEST')\n"
 '    def bar(x, y):\n'
 '        return x * y\n'
 '\n'
 '    umuus_redis_pubsub_mini.instance.run()\n'
 '    umuus_redis_pubsub_mini.instance.run(daemon=True)\n'
 '\n'
 '----\n'
 '\n'
 '    @umuus_redis_pubsub_mini.instance.subscribe(disable_on_completed=True)\n'
 '    def bar(x, y):\n'
 '        return x * y\n'
 '\n'
 '----\n'
 '\n'
 "    $ redis-cli --csv PSUBSCRIBE '*'\n"
 '\n'
 '    $ redis-cli PUBLISH \'umuus_redis_pubsub_mini.fn:on_next:1\' \'{"x": 2, '
 '"y": 3}\'\n'
 '\n'
 '----\n'
 '\n'
 '    $ python umuus_redis_pubsub_mini.py run --module my_module\n'
 '    $ python umuus_redis_pubsub_mini.py run --path my_module.foo\n'
 '\n'
 '----\n'
 '\n'
 'With Class\n'
 '----------\n'
 '\n'
 '    class Foo:\n'
 '        @classmethod\n'
 '        @instance.subscribe()\n'
 '        def test_classmethod(self, x, y=2):\n'
 '            return x * y\n'
 '\n'
 '        def test_method(self, x, y=2):\n'
 '            return x * y\n'
 '\n'
 '    instance.subscribe(Foo().test_method)\n'
 '\n'
 'Authors\n'
 '-------\n'
 '\n'
 '- Jun Makii <junmakii@gmail.com>\n'
 '\n'
 'License\n'
 '-------\n'
 '\n'
 'GPLv3 <https://www.gnu.org/licenses/>'),
    cmdclass={"pytest": PyTest},
)
