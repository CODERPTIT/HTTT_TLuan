#!/usr/bin/python
# -*- coding: UTF-8 -*-
from domain.order import Order
from domain.cart import Cart
from domain.order import Payment
from typing import List

class CheckoutService(object):
	def checkout(self, aCartId : int, aShippingAddress : str, aRecipientPhone : str) -> Order:
		pass

	def validateCart(self, aCart : Cart) -> long:
		pass

	def validateAvailability(self, aCart : Cart) -> long:
		pass

	def calculateTotal(self, aCart : Cart) -> Decimal:
		pass

	def createOrder(self, aCart : Cart, aShippingAddress : str, aRecipientPhone : str) -> Order:
		pass

	def processPayment(self, aOrder : Order) -> Payment:
		pass

	def confirmOrder(self, aOrder : Order) -> None:
		pass

	def releaseReservedStock(self, aCart : Cart) -> None:
		pass

