from setuptools import setup, find_packages


setup(
    name="echidna",
    version="0.0.1-dev",
    url='http://github.com/praekelt/echidna',
    license='BSD',
    description='A scalable pub-sub WebSocket service.',
    long_description=open('README.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekeltfoundation.org',
    packages=find_packages(),
    install_requires=[
        'Twisted',
        'cyclone',
        'txzookeeper',
        'redis',
        'PyYAML',
        'ws4py', # Strangely it's not enough to have this only in tests_require
    ],
    tests_require=[
        'ws4py',
        'requests',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Cyclone',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Communications',
        'Topic :: Internet',
        'Topic :: System :: Networking',
    ]
)
