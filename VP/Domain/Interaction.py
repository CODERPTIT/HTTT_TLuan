#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Domain import Customer
from Domain import Product
from Model2.Behavior import InteractionType
from typing import List

class Interaction(object):
	def interactionId(self) -> int:
		pass

	def interactionType(self) -> InteractionType:
		pass

	def interactedAt(self) -> datetime:
		pass

	def __init__(self):
		self._unnamed_Customer_ : Customer = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_Customer_2 : Customer = None
		"""# @AssociationMultiplicity 0..1"""
		self._unnamed_Product_ : Product = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_Product_2 : Product = None
		"""# @AssociationMultiplicity 1"""

