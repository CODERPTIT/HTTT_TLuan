#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

class WebContext(object):
	def render(self, aRequest, aName, aContext):
		pass

	def scope(self, aRequest, aImmediate : long):
		pass

	def currentAccount(self, aRequest, aServices):
		pass

	def requireRole(self, aRequest, aServices, aRoles):
		pass

	def customerId(self, aRequest, aServices) -> int:
		pass

	def optionalCustomerId(self, aRequest, aServices) -> int:
		pass

