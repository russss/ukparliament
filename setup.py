from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

version = {}
with open(path.join(here, 'ukparliament', "__init__.py")) as fp:
    exec(fp.read(), version)

with open('README.md') as f:
    long_description = f.read()

setup(name='ukparliament',
      version=version['__version__'],
      description='UK Parliament API Client',
      long_description=long_description,
      long_description_content_type='text/markdown',
      license='MIT',
      author='Russ Garrett',
      author_email='russ@garrett.co.uk',
      url='https://github.com/russss/ukparliament',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3 :: Only'
      ],
      keywords='parliament democracy uk',
      packages=['ukparliament'],
      install_requires=['requests', 'python-dateutil'],
      )
