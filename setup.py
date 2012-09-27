from distutils.core import setup

setup(
    name='CustomGAEAddons',
    version='0.1.0',
    packages=['cndb', 'tests'],
    url='',
    license='LICENSE.txt',
    author='neara',
    author_email='anatr@drykissoftdd.com',
    description='Adds useful properties to gae ndb.',
    long_desctiption=open('README.md').read(),
)
