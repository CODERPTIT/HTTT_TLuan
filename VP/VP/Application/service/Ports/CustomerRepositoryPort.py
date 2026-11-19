#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from domain.customer import Customer
from typing import List

class CustomerRepositoryPort(object):
	"""@Interface"""
	__metaclass__ = ABCMeta
	@abstractmethod
	def findById(self, aCustomerId : int) -> Customer:
		pass

