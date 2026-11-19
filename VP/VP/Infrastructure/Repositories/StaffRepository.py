#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

class StaffRepository(object):
	def products(self):
		pass

	def orders(self):
		pass

	def updateProduct(self, aProductId : int, aPrice : Decimal, aStatus : str):
		pass

	def updateStock(self, aProductId : int, aQuantity : int):
		pass

	def processOrder(self, aOrderId : int):
		pass

	def shipOrder(self, aOrderId : int):
		pass

	def report(self):
		pass

