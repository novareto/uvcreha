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
    'openapi_schema_pydantic',
    'orjson',
    'python-arango',
    'pydantic',
    'reg',
    'roughrider.auth',
    'roughrider.routing',
    'roughrider.validation',
    'wrapt',
    'wtforms',
]

test_requires = [
    'WebTest',
    'pytest',
    'pyyaml',
    'omegaconf',
    'docker',
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
