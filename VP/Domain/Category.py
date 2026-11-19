#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

class Category(object):
	def categoryId(self) -> int:
		pass

	def categoryName(self) -> str:
		pass

	def __init__(self):
		self._unnamed_Product_ = []
		"""# @AssociationMultiplicity 0..*"""
		self._unnamed_Product_2 = []
		"""# @AssociationMultiplicity 0..*"""

