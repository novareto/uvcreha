import os
from setuptools import setup, find_packages


version = "0.1"

install_requires = [
    'cromlech.session',
    'cromlech.sessions.file',
    'fanstatic',
    'horseman',
    'json_ref_dict',
    'jsonschema_rs',
    'jsonschema_wtforms',
    'py-vapid',
    'pyotp',
    'python-arango >= 7.1.0',
    'pywebpush',
    'qrcode[pil]',
    'reiter.amqp',
    'reiter.application',
    'reiter.arango',
    'reiter.form',
    'reiter.view',
    'repoze.vhm',
    'roughrider.contenttypes',
    'roughrider.events',
    'roughrider.routing',
    'roughrider.storage',
    'roughrider.workflow',
    'rutter',
    'wtforms',
    'wtforms_components',
]


test_requires = [
    'WebTest',
    'omegaconf',
    'pytest',
    'reiter.arango[test]',
    'reiter.startup'
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
        "pytest11": [
            "uvcreha = uvcreha.testing:pytest_uvcreha"
        ],
        "fanstatic.libraries": [
            "uvcreha = uvcreha.browser.resources:library",
        ],
    }
)
