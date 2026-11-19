#!/usr/bin/python
# -*- coding: UTF-8 -*-
from domain.order import Order
from typing import List

class CheckoutController(object):
	def checkout(self, aCartId : int, aShippingAddress : str, aRecipientPhone : str) -> Order:
		pass

