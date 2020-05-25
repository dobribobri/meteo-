# -*- coding: utf-8 -*-

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

ext = Extension(name='binaryparser',
                sources=['binaryparser.pyx'])
setup(version='0.1',
      author='Dobroslav P. Egorov, Mikhail T. Smirnov',
      description='Radiometric data calibration (C++-)module for python',
      ext_modules=cythonize(ext))
