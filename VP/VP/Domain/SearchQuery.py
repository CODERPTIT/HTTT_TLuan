#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from Domain import Customer
from typing import List

class SearchQuery(object):
	__metaclass__ = ABCMeta
	@classmethod
	def __init__(self):
		self._searchQueryId : int = None
		self._createdAt : datetime = None
		self._unnamed_Customer_ : Customer = None
		"""# @AssociationMultiplicity 1"""
		self._unnamed_SearchResult_ = []
		"""# @AssociationMultiplicity 0..*"""

