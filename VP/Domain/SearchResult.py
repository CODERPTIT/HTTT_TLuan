#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Domain import SearchQuery
from Domain import Product
from typing import List

class SearchResult(object):
	def rank(self) -> int:
		pass

	def relevanceScore(self) -> Decimal:
		pass

	def __init__(self):
		self._unnamed_SearchQuery_ : SearchQuery = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_Product_ : Product = None
		"""# @AssociationMultiplicity 1"""

