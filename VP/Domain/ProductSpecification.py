#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Domain import Product
from typing import List

class ProductSpecification(object):
	def specificationId(self) -> int:
		pass

	def specName(self) -> str:
		pass

	def specValue(self) -> str:
		pass

	def __init__(self):
		self._unnamed_Product_ : Product = None
		"""# @AssociationMultiplicity 1
		# @AssociationKind Composition"""
		self._unnamed_Product_2 : Product = None
		"""# @AssociationMultiplicity 1"""

