#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:35:16 2020

@author: harshpujari
"""

import hmac
import hashlib


class Checksum:

    def calculateChecksum(secret_key, checksumString):
        #Uses an HMAC SHA-256 algorithm to calculate the checksum of the data passed.
        
        secret_key = bytes(secret_key,"utf-8")
        total_params = bytes(checksumString,"utf-8")
        checksum = hmac.new(secret_key, total_params, hashlib.sha256).hexdigest()
        return checksum

    
    def getChecksumString(params):
        checksumString = ""
        for param in sorted(params.keys()):
            checksumString = str(checksumString+param)+"="+str(params[param])+"&"
        return checksumString
    
    
    def getUpdateChecksumString(params):
        checksumString = ""
        for param in params.keys():
            checksumString = checksumString+'\''+str(params[param])+'\''
        return checksumString
    