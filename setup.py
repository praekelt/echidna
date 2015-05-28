from setuptools import setup, find_packages


setup(
    name="echidna",
    version="0.0.15",
    url='http://github.com/praekelt/echidna',
    license='BSD',
    description='A scalable pub-sub WebSocket service.',
    long_description=open('README.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekeltfoundation.org',
    packages=[
        "echidna",
        "twisted.plugins",
    ],
    package_data={
        'twisted.plugins': ['twisted/plugins/echidna_plugin.py'],
    },
    include_package_data=True,
    install_requires=[
        'Twisted>=14.0.2',
        'autobahn>=0.9.3',
        'txzookeeper',
        'redis',
        'PyYAML',
        'cryptography',
        'ws4py', # Strangely it's not enough to have this only in tests_require
        'requests',
        'dateutils',
        'pika',
        'treq'
    ],
    tests_require=[
        'ws4py',
        'requests',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Communications',
        'Topic :: Internet',
        'Topic :: System :: Networking',
    ]
)
