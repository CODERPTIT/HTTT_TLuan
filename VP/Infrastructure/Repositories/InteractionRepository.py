#!/usr/bin/python
# -*- coding: UTF-8 -*-
import Interaction
import Product
from Model2.Behavior import InteractionType
from Application.service.Ports import InteractionRepositoryPort
from typing import List

class InteractionRepository(InteractionRepositoryPort):
	def findByCustomer(self, aCustomerId : int) -> List:
		pass

	def findByProduct(self, aProductId : int) -> List:
		pass

	def listAll(self) -> List:
		pass

	def save(self, aInteraction : Interaction) -> None:
		pass

	def record(self, aCustomerId : int, aProduct : Product, aKind : InteractionType) -> None:
		pass

