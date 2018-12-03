#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name = 'mpg',
    packages = find_packages(),
    version = '0.0.1',
    description = 'To generate MaaS pods',
    author = 'Taihsiang Ho (tai271828)',
    author_email = 'tai271828@gmail.com',
    url = 'https://github.com/tai271828/maas-pod-generator',
    download_url = 'https://github.com/tai271828/maas-pod-generator',
    keywords = ['ubuntu', 'maas', 'science', 'cluster'],
    entry_points={
        'console_scripts': [
            'mpg-cli=mpg.launcher.mpg_cli:main',
        ]
    },
    classifiers = [
        "Programming Language :: Python",
    ]
)
