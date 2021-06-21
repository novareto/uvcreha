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
    'pyotp',
    'pywebpush',
    'qrcode[pil]',
    'reiter.application',
    'reiter.arango',
    'reiter.form',
    'reiter.view',
    'roughrider.contenttypes',
    'roughrider.events',
    'roughrider.routing',
    'roughrider.workflow',
    'wtforms',
    'wtforms_components',
]


test_requires = [
    'WebTest',
    'horsebox',
    'omegaconf',
    'pytest',
    'pyhamcrest',
    'reiter.arango[test]',
    'reiter.amqp',
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
