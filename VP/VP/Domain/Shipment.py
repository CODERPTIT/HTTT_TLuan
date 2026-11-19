#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Domain import Order
from Domain import ShippingProvider
from Model2.Ordering import ShipmentStatus
from typing import List

class Shipment(object):
	def trackingNumber(self) -> str:
		pass

	def status(self) -> ShipmentStatus:
		pass

	def carrier(self) -> str:
		pass

	def estimatedDeliveryDate(self) -> datetime:
		pass

	def deliveredAt(self) -> datetime:
		pass

	def __orderId(self) -> int:
		pass

	def shippingProviderId(self) -> int:
		pass

	def __init__(self):
		self._unnamed_Order_ : Order = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_ShippingProvider_ : ShippingProvider = None
		"""# @AssociationMultiplicity 0..1"""
		self._unnamed_ShippingProvider_2 = []
		"""# @AssociationMultiplicity 0..*"""
		self._unnamed_ShippingProvider2_ = []
		"""# @AssociationMultiplicity 0..*"""
		self._unnamed_ShippingProvider3_ = []
		"""# @AssociationMultiplicity 0..*"""
		self._unnamed_Order_2 : Order = None
		"""# @AssociationMultiplicity 1"""

