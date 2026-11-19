#!/usr/bin/python
# -*- coding: UTF-8 -*-
from domain.cart import Cart
from typing import List

class CartService(object):
	def getCart(self, aCustomerId : int) -> Cart:
		pass

	def addItem(self, aCartId : int, aProductId : int, aQuantity : int) -> Cart:
		pass

	def updateQuantity(self, aCartId : int, aProductId : int, aQuantity : int) -> Cart:
		pass

	def removeItem(self, aCartId : int, aProductId : int) -> Cart:
		pass

