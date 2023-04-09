from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# exec(open(read('codebrain/version.py')).read())
print('packages:', [package for package in find_packages()
                if package.startswith('codebrain')])
setup(
    name='codebrain', 
    # version=__version__, 
    version='0.0.1',
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
    install_requires=[
        'IPython',
        'traitlets',
        'notebook>=5.7.6',
    ],
    author='codebrain',
    author_email='codebrain@codebrain.app',
)