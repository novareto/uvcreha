import os
from setuptools import setup, find_packages


version = "0.1"

install_requires = [
    'bjoern',
    'blinker',
    'chameleon',
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
    'reiter.arango',
    'reiter.form',
    'reiter.routing',
    'roughrider.auth',
    'roughrider.workflow',
    'rutter',
    'wrapt',
    'wtforms',
    'wtforms_pydantic',
]


test_requires = [
    'WebTest',
    'omegaconf',
    'pyhamcrest',
    'pytest',
    'pyyaml',
    'reiter.arango[test]',
]


setup(
    name='docmanager',
    version=version,
    author='Novareto GmbH',
    author_email='contact@example.com',
    url='http://www.example.com',
    download_url='',
    description='Docmanager WebSite',
    long_description=(open("README.txt").read() + "\n" +
                      open(os.path.join("docs", "HISTORY.txt")).read()),
    license='ZPL',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python:: 3 :: Only',
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'test': test_requires,
    },
    entry_points={
        'chameleon.tales': [
            'slot = docmanager.browser.slot:SlotExpr',
        ],
        'fanstatic.libraries': [
            'docmanager = docmanager.browser.resources:library',
        ]
    }
)
