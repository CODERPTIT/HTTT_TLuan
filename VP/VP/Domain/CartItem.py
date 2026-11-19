#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Domain import Cart
from Domain import Product
from typing import List

class CartItem(object):
	def cartItemId(self) -> int:
		pass

	def quantity(self) -> int:
		pass

	def __init__(self):
		self._unnamed_Cart_ : Cart = None
		"""# @AssociationMultiplicity 1
		# @AssociationKind Composition"""
		self._unnamed_Cart_2 : Cart = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_Product_ : Product = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_Product_2 : Product = None
		"""# @AssociationMultiplicity 1"""

