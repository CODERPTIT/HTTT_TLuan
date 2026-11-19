#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Domain import Customer
from Domain import Shipment
from Domain import Payment
from Model2.Ordering import OrderStatus
from typing import List

class Order(object):
	def orderId(self) -> int:
		pass

	def shippingAddress(self) -> str:
		pass

	def recipientPhone(self) -> str:
		pass

	def customerId(self) -> int:
		pass

	def orderDate(self) -> datetime:
		pass

	def status(self) -> OrderStatus:
		pass

	def updateStatus(self, aStatus : OrderStatus) -> None:
		pass

	def __init__(self):
		self._unnamed_Customer_ : Customer = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_Shipment_ : Shipment = None
		"""# @AssociationMultiplicity 0..1"""
		self._unnamed_Payment_ : Payment = None
		"""# @AssociationMultiplicity 0..1"""
		self._unnamed_Customer_2 : Customer = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_OrderItem_ = []
		"""# @AssociationMultiplicity 1..*"""
		self._unnamed_Payment_2 : Payment = None
		"""# @AssociationMultiplicity 0..1"""
		self._unnamed_Shipment_2 : Shipment = None
		"""# @AssociationMultiplicity 0..1"""
		self._unnamed_OrderItem_2 = []
		"""# @AssociationMultiplicity 1..*
		# @AssociationKind Composition"""

