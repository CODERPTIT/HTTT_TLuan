#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

class AccountRepository(object):
	def findById(self, aAccountId : int):
		pass

	def authenticate(self, aEmail : str, aPassword : str):
		pass

	def profile(self, aAccountId : int, aIncludeStats : long):
		pass

	def updateCustomerProfile(self, aAccountId : int, aName : str, aPhone : str, aAddress : str):
		pass

	def registerCustomer(self, aName : str, aEmail : str, aPassword : str):
		pass

