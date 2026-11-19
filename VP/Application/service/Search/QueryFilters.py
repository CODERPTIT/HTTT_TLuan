#!/usr/bin/python
# -*- coding: UTF-8 -*-
import Product
from typing import List

class QueryFilters(object):
	def parse(self, aText : str, aProducts : List) -> QueryFilters:
		pass

	def accepts(self, aProduct : Product) -> long:
		pass

