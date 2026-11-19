#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Domain import Order
from Domain import Product
from typing import List

class OrderItem(object):
	def orderItemId(self) -> int:
		pass

	def quantity(self) -> int:
		pass

	def __init__(self):
		self._unnamed_Order_ : Order = None
		"""# @AssociationMultiplicity 1
		# @AssociationKind Composition"""
		self._unnamed_Order_2 : Order = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_Product_ : Product = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_Product_2 : Product = None
		"""# @AssociationMultiplicity 1"""

