#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Domain import ShippingProvider
from typing import List

class User(object):
	def userId(self) -> int:
		pass

	def fullName(self) -> str:
		pass

	def email(self) -> str:
		pass

	def phoneNumber(self) -> str:
		pass

	def role(self) -> str:
		pass

	def active(self) -> long:
		pass

	def __init__(self):
		self._unnamed_ShippingProvider_ : ShippingProvider = None
		"""# @AssociationMultiplicity 0..1"""

