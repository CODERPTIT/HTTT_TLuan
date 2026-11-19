#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Domain import User
from typing import List

class ShippingProvider(object):
	def shippingProviderId(self) -> int:
		pass

	def providerCode(self) -> str:
		pass

	def providerName(self) -> str:
		pass

	def supportEmail(self) -> str:
		pass

	def supportPhone(self) -> str:
		pass

	def address(self) -> str:
		pass

	def active(self) -> long:
		pass

	def __init__(self):
		self._unnamed_User_ : User = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_Shipment_ = []
		"""# @AssociationMultiplicity 0..*"""

