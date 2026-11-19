#!/usr/bin/python
# -*- coding: UTF-8 -*-
from domain.order import Order
from typing import List

class OrderRepository(object):
	def findById(self, aOrderId : int) -> Order:
		pass

	def findByCustomer(self, aCustomerId : int) -> List:
		pass

	def save(self, aOrder : Order) -> None:
		pass

	def update(self, aOrder : Order) -> None:
		pass

