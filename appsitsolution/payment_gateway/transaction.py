#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:29:35 2020

@author: harshpujari
"""

from .RequestParameters import RequestParameters
from portal_auretics_com import settings
from .ChecksumGenerator import Checksum
import webbrowser


class Transactions :
    
    def processTransaction():
        
        #You can also pass these parameters as function arguments
        requestParams = RequestParameters.getProcessTransactionParameters()
        
        requestUrl = settings.ENVIRONMENT + settings.TRANSACTION_API_URL
        
        checksumString = Checksum.getChecksumString(requestParams)
        
        checksum = Checksum.calculateChecksum(settings.ZAAKPAY_SECRET_KEY , checksumString)
        
        #Above are all the request parameters you need to pass to initiate transaction
        #You need to post all the parameters with checksum to the request URL
        
        if settings.DEMO :
            print("Final Request : "+requestUrl+"?"+checksumString+"checksum="+checksum)
            webbrowser.open(requestUrl+"?"+checksumString+"checksum="+checksum)

        
    def checkTransactionStatus(orderId):
        
        #You can also pass these parameters as function arguments
        requestParams = RequestParameters.getTransactionStatusParameters(orderId)
        
        requestUrl = settings.ENVIRONMENT + settings.TRANSACTION_STATUS_API_URL
        
        data = requestParams['formRequestData']
        
        checksum = Checksum.calculateChecksum(settings.ZAAKPAY_SECRET_KEY , data)
        
        #Above are all the request parameters you need to pass to check transaction status
        #You need to post all the parameters with checksum to the request URL
        
        if settings.DEMO :
            #You need to post the below request as FORM POST Method
            #Also the data needs should be in URL_Encoded form
            print("Final Request : "+requestUrl+"&data="+data+"&checksum="+checksum)        


    def partialRefund(orderId,amount):
        
        #You can also pass these parameters as function arguments
        requestParams = RequestParameters.getPartialRefundParameters(orderId,amount)
        
        requestUrl = settings.ENVIRONMENT + settings.UPDATE_API_URL

        checksumString = Checksum.getUpdateChecksumString(requestParams)        
        
        checksum = Checksum.calculateChecksum(settings.ZAAKPAY_SECRET_KEY , checksumString)
        
        #Above are all the request parameters you need to pass to check transaction status
        #You need to post all the parameters with checksum to the request URL
        
        if settings.DEMO :
            #You need to post all the request parametes that you get from above
            print("Final Request : "+requestUrl+"\n Checksum String : "+checksumString+"\n checksum="+checksum)        
        

    def fullRefund(orderId):
        
        #You can also pass these parameters as function arguments
        requestParams = RequestParameters.getFullRefundParameters(orderId)
        
        requestUrl = settings.ENVIRONMENT + settings.UPDATE_API_URL

        checksumString = Checksum.getUpdateChecksumString(requestParams)        
        
        checksum = Checksum.calculateChecksum(settings.ZAAKPAY_SECRET_KEY , checksumString)
        
        #Above are all the request parameters you need to pass to check transaction status
        #You need to post all the parameters with checksum to the request URL
        
        if settings.DEMO :
            #You need to post all the request parametes that you get from above
            print("Final Request : "+requestUrl+"\n Checksum String : "+checksumString+"\n checksum="+checksum)        
        

#You can use the below function to go through the payment experience 
#Currently final page is of Zaakpay's testing page which you can change using the returnUrl

#Transaction.processTransaction()