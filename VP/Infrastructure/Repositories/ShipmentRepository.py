#!/usr/bin/python
# -*- coding: UTF-8 -*-
from domain.order import Shipment
from typing import List

class ShipmentRepository(object):
	def findByOrder(self, aOrderId : int) -> Shipment:
		pass

	def findByTrackingNumber(self, aTrackingNumber : str) -> Shipment:
		pass

	def defaultProviderId(self) -> int:
		pass

	def save(self, aShipment : Shipment) -> None:
		pass

	def update(self, aShipment : Shipment) -> None:
		pass

