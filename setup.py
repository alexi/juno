from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

exec(open(read('version.py')).read())

setup(
    name='codebrain', 
    version=__version__, 
    packages=[package for package in find_packages()
                if package.startswith('codebrain')], 
    long_description=read('README.md'),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Multimedia :: Graphics',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': [
            'codebrain = codebrain:run'
        ]
    },
    install_requires=[
        'IPython',
        'traitlets',
        'notebook>=5.7.6',
    ],
    author='codebrain',
    author_email='codebrain@codebrain.app',
    packages=find_packages(),
)