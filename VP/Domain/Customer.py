#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Domain import Cart
import User
import User2
import User3
from Domain import User
from typing import List

class Customer(User, User2, User3, User):
	def __init__(self):
		self._deliveryAddress : str = None
		self._unnamed_SearchQuery_ = []
		"""# @AssociationMultiplicity 0..*"""
		self._unnamed_Interaction_ = []
		"""# @AssociationMultiplicity 0..*"""
		self._unnamed_Cart_ : Cart = None
		"""# @AssociationMultiplicity 0..1"""
		self._unnamed_Order_ = []
		"""# @AssociationMultiplicity 0..*"""
		self._unnamed_Interaction_2 = []
		"""# @AssociationMultiplicity 0..*"""
		self._unnamed_Order_2 = []
		"""# @AssociationMultiplicity 0..*"""
		self._unnamed_Cart_2 : Cart = None
		"""# @AssociationMultiplicity 0..1"""

