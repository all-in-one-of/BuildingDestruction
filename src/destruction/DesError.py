# -*- coding: utf-8 -*-
'''
Created on Nov 3, 2010

@author: carlos
'''

class DesError(object):
    '''
    Class for manage errors in the program
    '''
    def __init__(self):
        self.code = []
        self.listOfErrors = []
        #0
        self.listOfErrors.append("No error")
        #1
        self.listOfErrors.append("Impossible interprimitive path cause of bad inicial point")
        #2
        self.listOfErrors.append("Impossible interprimitive path")
        #3
        self.listOfErrors.append("No building initialice")

    def setCode(self, newCode):
        self.code.append(newCode)

    def __str__(self):
        for code in self.code:
            print self.listOfErrors[code]
