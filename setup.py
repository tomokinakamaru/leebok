import os
from setuptools import setup, find_namespace_packages


def readme():
    with open('README.md') as f:
        return f.read()


def version():
    def find(root):
        for path, _, files in os.walk(root):
            for file in files:
                if file == 'version.py':
                    return os.path.join(path, file)

    def read(path):
        with open(path) as fp:
            for line in fp:
                if line.startswith(('major', 'minor', 'patch')):
                    yield line.split('=')[-1].strip()

    return '.'.join(read(find('src')))


pkgs = find_namespace_packages('src')

name = pkgs[0]

setup(
    author_email='tomoki.nakamaru@gmail.com',
    author='Tomoki Nakamaru',
    entry_points={'console_scripts': [f'{name}={name}.__main__:main']},
    install_requires=[
        'boto3',
        'cached-property',
        'pyparsing',
        'pyyaml'
    ],
    long_description_content_type='text/markdown',
    long_description=readme(),
    name=name,
    package_dir={'': 'src'},
    packages=pkgs,
    python_requires='>=3',
    version=version()
)
