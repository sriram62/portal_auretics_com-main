#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:35:36 2020

@author: harshpujari
"""

import time
from portal_auretics_com import settings


class RequestParameters:

    def getProcessTransactionParameters():
        amount = 100
        orderId = "ZPLive" + str(round(time.time()))
        merchantIdentifier = settings.ZAAKPAY_MERCHANT_IDENTIFIER
        currency = "INR"
        buyerEmail = "ooa@auretics.com"
        # Add all the parameters ( Mandatory/Optional ) here
        params = {"amount": amount, "merchantIdentifier": merchantIdentifier, "orderId": orderId,
                  "currency": currency, "buyerEmail": buyerEmail}
        return params

    def getTransactionStatusParameters(orderId):
        merchantIdentifier = settings.ZAAKPAY_MERCHANT_IDENTIFIER
        mode = "0"

        # You can also pass JSON object here to submit in final form request or you can use the below format string
        params = {"orderId": orderId, "merchantIdentifier": merchantIdentifier, "mode": mode,
                  "formRequestData": "{merchantIdentifier:" + merchantIdentifier + ",mode:" + mode + ",orderDetail:{orderId:" + orderId + "}}"}

        return params

    def getPartialRefundParameters(orderId, amount):
        merchantIdentifier = settings.ZAAKPAY_MERCHANT_IDENTIFIER
        mode = "0"
        updateDesired = "22"
        updateReason = "Test reason"

        # The checksum string would be generated in the same way
        # Also post the parameters in the same way
        params = {"merchantIdentifier": merchantIdentifier, "orderId": orderId, "mode": mode,
                  "updateDesired": updateDesired, "updateReason": updateReason, "amount": amount}

        return params

    def getFullRefundParameters(orderId):
        merchantIdentifier = settings.ZAAKPAY_MERCHANT_IDENTIFIER
        mode = "0"
        updateDesired = "14"
        updateReason = "Test reason"

        # The checksum string would be generated in the same way
        # Also post the parameters in the same way
        params = {"merchantIdentifier": merchantIdentifier, "orderId": orderId, "mode": mode,
                  "updateDesired": updateDesired, "updateReason": updateReason}

        return params
