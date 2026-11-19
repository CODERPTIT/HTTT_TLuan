#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Domain import Category
from Domain import Inventory
from Model2.Catalog import ProductStatus
from typing import List

class Product(object):
	def productId(self) -> int:
		pass

	def productName(self) -> str:
		pass

	def description(self) -> str:
		pass

	def price(self) -> Decimal:
		pass

	def status(self) -> ProductStatus:
		pass

	def quantityAvailable(self) -> int:
		pass

	def isAvailable(self, aQuantity : int) -> long:
		pass

	def reserve(self, aQuantity : int) -> long:
		pass

	def release(self, aQuantity : int) -> None:
		pass

	def searchableText(self) -> str:
		pass

	def __init__(self):
		self._unnamed_SearchResult_ = []
		"""# @AssociationMultiplicity 0..*"""
		self._unnamed_Interaction_ = []
		"""# @AssociationMultiplicity 0..*"""
		self._unnamed_CartItem_ = []
		"""# @AssociationMultiplicity 0..*"""
		self._unnamed_OrderItem_ = []
		"""# @AssociationMultiplicity 0..*"""
		self._unnamed_Category_ : Category = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_ProductUnit_ = []
		"""# @AssociationMultiplicity 0..*"""
		self._unnamed_Category_2 : Category = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_CartItem_2 = []
		"""# @AssociationMultiplicity 0..*"""
		self._unnamed_Interaction_2 = []
		"""# @AssociationMultiplicity 0..*"""
		self._unnamed_ProductSpecification_ = []
		"""# @AssociationMultiplicity 1..*"""
		self._unnamed_Inventory_ : Inventory = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_ProductUnit_2 = []
		"""# @AssociationMultiplicity 0..*"""
		self._unnamed_ProductSpecification_2 = []
		"""# @AssociationMultiplicity 1..*
		# @AssociationKind Composition"""
		self._unnamed_OrderItem_2 = []
		"""# @AssociationMultiplicity 0..*"""

