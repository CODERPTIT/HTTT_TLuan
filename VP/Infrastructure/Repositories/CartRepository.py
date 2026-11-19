#!/usr/bin/python
# -*- coding: UTF-8 -*-
from domain.cart import Cart
from typing import List

class CartRepository(object):
	def findById(self, aCartId : int) -> Cart:
		pass

	def findByCustomer(self, aCustomerId : int) -> Cart:
		pass

	def save(self, aCart : Cart) -> None:
		pass

	def update(self, aCart : Cart) -> None:
		pass

