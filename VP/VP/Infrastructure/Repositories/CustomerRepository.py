#!/usr/bin/python
# -*- coding: UTF-8 -*-
from domain.customer import Customer
from Application.service.Ports import CustomerRepositoryPort
from typing import List

class CustomerRepository(CustomerRepositoryPort):
	def findById(self, aCustomerId : int) -> Customer:
		pass

