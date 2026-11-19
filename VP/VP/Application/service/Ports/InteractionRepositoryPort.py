#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
import Product
from Model2.Behavior import InteractionType
from typing import List

class InteractionRepositoryPort(object):
	"""@Interface"""
	__metaclass__ = ABCMeta
	@abstractmethod
	def findByCustomer(self, aCustomerId : int) -> List:
		pass

	@abstractmethod
	def listAll(self) -> List:
		pass

	@abstractmethod
	def record(self, aCustomerId : int, aProduct : Product, aKind : InteractionType) -> None:
		pass

