# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#
# distutils: language = c++

from libcpp.string cimport string
from termcolor import colored

cdef extern from "c_binaryparser.cpp":
    cdef void c_parse(string fPath, string cPath, string outPath)

def parse(fPath, cPath, outPath):
    c_parse(fPath.encode(), cPath.encode(), outPath.encode())
    print('Записано: {}\t'.format(outPath) + '[' + colored('OK', 'green') + ']')
    return
