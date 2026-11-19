#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Domain import Inventory
from Domain import Product
from typing import List

class ProductUnit(object):
	def serialNumber(self) -> str:
		pass

	def __init__(self):
		self._unnamed_Inventory_ : Inventory = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_Product_ : Product = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_Product_2 : Product = None
		"""# @AssociationMultiplicity 1"""

