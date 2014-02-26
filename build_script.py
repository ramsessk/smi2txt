#!/bin/python

import os,sys
import shlex
from subprocess import Popen, PIPE, call #@UnusedImport


pkg_name = "smi2txt"
doc_files = "docs"
doc_build_dest = "_build"
doc_build_src = "doc"
RELEASE_DIR = "Release"

def shlep(cmd="", env=None):
    '''shlex split and popen
    '''
    parsed_cmd = shlex.split(cmd)
    #print parsed_cmd
    #ret = call(parsed_cmd)
    p = Popen(parsed_cmd, env=env)
    p.communicate()
    ret = p.returncode
    return ret

# Find script directory
_dname = os.path.dirname(os.path.realpath(__file__))
pkg_loc = _dname + os.path.sep+pkg_name 
sys.path.append(pkg_loc)


# Check installation of Sphinx, setuptools
try:
    import sphinx
except:
    print("sphinx is not installed")
    sys.exit(1)
print("sphinx version is {0}".format(sphinx.__version__))

try:
    import setuptools
except:
    print("setuptools is not installed")
    sys.exit(1)
print("setuptools version is {0}".format(setuptools.__version__))

"""
sphinx_src = _dname + os.path.sep + pkg_name + os.path.sep+doc_build_src
sphinx_dest = sphinx_src + os.path.sep+doc_build_dest
cmd = 'rm -rf ' + sphinx_dest
if os.path.exists(sphinx_dest):
    print ('deleting:{0}'.format(sphinx_dest))
    ret = shlep(cmd)

# Add new PATH environ value because sphnix import new package to read
# doc string.
print("Running sphinx ...")
new_env = os.environ.copy()
new_env["PATH"] = _dname + ':' + new_env["PATH"]
cmd = 'sphinx-build -b singlehtml ' + sphinx_src + ' ' + sphinx_dest
ret = shlep(cmd, env= new_env)
if ret !=0 :
    print("error found")
    sys.exit()

print ("Copying document files ...")
sphinx_docfiles = _dname + os.path.sep + pkg_name + os.path.sep+doc_files
if os.path.exists(sphinx_docfiles):
    cmd = 'rm -rf ' + sphinx_docfiles
    ret = shlep(cmd)

cmd = 'mkdir ' + sphinx_docfiles
ret = shlep(cmd)

cmd = 'cp -v ' + sphinx_dest + os.path.sep + pkg_name + ".html " + sphinx_docfiles
ret = shlep(cmd)

cmd = 'cp -R -v ' + sphinx_dest + os.path.sep + '_static' + os.path.sep + \
        ' ' + sphinx_docfiles + os.path.sep + '_static'
ret = shlep(cmd)
"""

# setup.py absolute path
setup_file = _dname + os.path.sep + 'setup.py'

print ("Building {0} package ...".format(pkg_name))
dist = _dname + os.path.sep + RELEASE_DIR
if not os.path.exists(dist):
    cmd = 'mkdir ' + dist
    shlep(cmd)

cmd = 'python setup.py bdist_egg --dist-dir ' + dist
ret = shlep(cmd)

egg_dir = _dname + os.path.sep + pkg_name + '.egg-info' + os.path.sep
if os.path.exists(egg_dir):
    cmd = 'rm -rf ' + egg_dir
    ret = shlep(cmd)


