#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

class StaffService(object):
	def products(self):
		pass

	def orders(self):
		pass

	def updateProduct(self, aProductId : int, aPrice : Decimal, aStatus : str) -> None:
		pass

	def updateStock(self, aProductId : int, aQuantity : int) -> None:
		pass

	def processOrder(self, aOrderId : int) -> None:
		pass

	def shipOrder(self, aOrderId : int) -> None:
		pass

	def report(self):
		pass

