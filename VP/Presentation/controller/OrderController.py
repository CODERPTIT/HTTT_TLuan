#!/usr/bin/python
# -*- coding: UTF-8 -*-
from domain.order import Order
from domain.order import Shipment
from domain.order import Payment
from typing import List

class OrderController(object):
	def viewOrder(self, aOrderId : int) -> Order:
		pass

	def trackOrder(self, aOrderId : int) -> Shipment:
		pass

	def getPayment(self, aOrderId : int) -> Payment:
		pass

	def listOrders(self, aCustomerId : int) -> List:
		pass

