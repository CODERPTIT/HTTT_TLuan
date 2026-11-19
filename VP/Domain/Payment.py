#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Domain import Order
from Model2.Ordering import PaymentStatus
from typing import List

class Payment(object):
	def paymentId(self) -> int:
		pass

	def paymentMethod(self) -> str:
		pass

	def amount(self) -> Decimal:
		pass

	def status(self) -> PaymentStatus:
		pass

	def transactionCode(self) -> str:
		pass

	def paidAt(self) -> datetime:
		pass

	def __orderId(self) -> int:
		pass

	def __init__(self):
		self._unnamed_Order_ : Order = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_Order_2 : Order = None
		"""# @AssociationMultiplicity 1"""

