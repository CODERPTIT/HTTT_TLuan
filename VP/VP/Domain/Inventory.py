#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Domain import Product
from typing import List

class Inventory(object):
	def isAvailable(self, aQuantity : int) -> long:
		pass

	def reserve(self, aQuantity : int) -> long:
		pass

	def release(self, aQuantity : int) -> None:
		pass

	def increaseStock(self, aQuantity : int) -> None:
		pass

	def decreaseStock(self, aQuantity : int) -> None:
		pass

	def __init__(self):
		self.___inventoryId : Long = None
		self.___quantityAvailable : int = None
		self._unnamed_Product_ : Product = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_ProductUnit_ = []
		"""# @AssociationMultiplicity 0..*"""

