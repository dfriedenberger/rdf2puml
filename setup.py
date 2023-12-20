from setuptools import setup
from rdf2puml import __version__

setup(name='rdf2puml',
      version=__version__,
      description='Tool for Creating plantuml Files from rdf model.',
      long_description=open('README.md', encoding="UTF-8").read(),
      long_description_content_type='text/markdown',
      url='https://github.com/dfriedenberger/rdf2puml.git',
      author='Dirk Friedenberger',
      author_email='projekte@frittenburger.de',
      license='GPLv3',
      packages=['rdf2puml'],
      scripts=['bin/rdf2puml'],
      install_requires=['rdflib', 'obse'],
      classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
      ],
      zip_safe=False)
