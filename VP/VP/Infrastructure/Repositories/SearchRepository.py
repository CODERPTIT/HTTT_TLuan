#!/usr/bin/python
# -*- coding: UTF-8 -*-
import SearchQuery
from typing import List

class SearchRepository(object):
	def save(self, aQuery : SearchQuery, aResults : List, aCustomerId : int) -> None:
		pass

	def findById(self, aSearchQueryId : int) -> SearchQuery:
		pass

	def findByCustomer(self, aCustomerId : int) -> List:
		pass

	def findResults(self, aSearchQueryId : int) -> List:
		pass

