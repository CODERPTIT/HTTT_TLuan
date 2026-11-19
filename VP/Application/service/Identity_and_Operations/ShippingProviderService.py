#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

class ShippingProviderService(object):
	def shipments(self, aProviderId : int):
		pass

	def markOutForDelivery(self, aProviderId : int, aOrderId : int) -> None:
		pass

	def markDelivered(self, aProviderId : int, aOrderId : int) -> None:
		pass

