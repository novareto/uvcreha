import os
from setuptools import setup, find_packages


version = "0.1"

install_requires = [
    'bjoern',
    'chameleon',
    'colorlog',
    'dramatiq[rabbitmq,redis]',
    'cromlech.jwt',
    'cromlech.session',
    'cromlech.sessions.file',
    'fanstatic',
    'horseman',
    'kombu',
    'openapi_schema_pydantic',
    'orjson',
    'py-vapid',
    'pydantic[email]',
    'python-arango',
    'pywebpush',
    'reg',
    'reiter.application',
    'reiter.arango',
    'reiter.form',
    'reiter.view',
    'roughrider.auth',
    'roughrider.predicate',
    'roughrider.routing',
    'roughrider.workflow',
    'rutter',
    'wrapt',
    'wtforms',
    'wtforms_pydantic',
    'zope.dottedname',
]


test_requires = [
    'WebTest',
    'omegaconf',
    'pyhamcrest',
    'pytest',
    'pyyaml',
    'pytest-cov',
    'reiter.arango[test]',
]


setup(
    name='uvcreha',
    version=version,
    author='Novareto GmbH',
    author_email='contact@example.com',
    url='http://www.example.com',
    download_url='',
    description='Uvcreha WebSite',
    long_description=(open("README.txt").read() + "\n" +
                      open(os.path.join("docs", "HISTORY.txt")).read()),
    license='ZPL',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python:: 3 :: Only',
    ],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    setup_requires=['pytest-runner'],
    tests_require=test_requires,
    extras_require={
        'test': test_requires,
    },
    entry_points={
        'fanstatic.libraries': [
            'uvcreha = uvcreha.browser.resources:library',
        ]
    }
)
