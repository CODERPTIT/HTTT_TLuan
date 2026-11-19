#!/usr/bin/python
# -*- coding: UTF-8 -*-
from domain.order import Payment
from typing import List

class PaymentRepository(object):
	def findByOrder(self, aOrderId : int) -> Payment:
		pass

	def save(self, aPayment : Payment) -> None:
		pass

	def update(self, aPayment : Payment) -> None:
		pass

