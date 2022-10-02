# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 08:07:28 2022

@author: nitsu
"""
import pip
info=open('requirements.txt','r')
packages=[x.strip() for x in info.readlines()]
for package in packages:
    pip.main(['install',package])