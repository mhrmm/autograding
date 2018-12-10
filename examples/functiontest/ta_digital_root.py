#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 16:27:56 2018

@author: hopkinsm
"""

def digital_root(n):
    while n >= 10:
        digits = [int(x) for x in list(str(n))]
        n = sum(digits)
    return n
