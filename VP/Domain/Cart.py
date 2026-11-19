#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Domain import Customer
from Domain import CartItem
from Domain import Product
from typing import List

class Cart(object):
	def cartId(self) -> int:
		pass

	def customerId(self) -> int:
		pass

	def createdAt(self) -> datetime:
		pass

	def findItem(self, aProduct : Product) -> CartItem:
		pass

	def addItem(self, aProduct : Product, aQuantity : int) -> None:
		pass

	def removeItem(self, aProduct : Product) -> None:
		pass

	def updateQuantity(self, aProduct : Product, aQuantity : int) -> None:
		pass

	def calculateTotal(self) -> Decimal:
		pass

	def isEmpty(self) -> long:
		pass

	def __init__(self):
		self._unnamed_Customer_ : Customer = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_Customer_2 : Customer = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_CartItem_ = []
		"""# @AssociationMultiplicity 0..*"""
		self._unnamed_CartItem_2 = []
		"""# @AssociationMultiplicity 1..*
		# @AssociationKind Composition"""

