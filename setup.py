from smi2txt_ezsetup import use_setuptools
use_setuptools()
from setuptools import setup

#from setuptools import setup

setup(name='smi2txt',
      version='1.3.2',
      author='Steven',
      author_email='ramsessk@gmail.com',
      url='https://github.com/ramsessk/smi2txt.git',
      description='smi to srt, smi to txt converter',
      long_description=open('readme.md').read(),
      packages = ['smi2txt'],
      package_dir={'smi2txt': 'src'},
      package_data={'smi2txt': ['smi2txt.py', '*.py']}
      )
