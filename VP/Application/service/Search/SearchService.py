#!/usr/bin/python
# -*- coding: UTF-8 -*-
import SearchQuery
import Product
from typing import List

class SearchService(object):
	def search(self, aQuery : SearchQuery) -> List:
		pass

	def validateInput(self, aQuery : SearchQuery) -> long:
		pass

	def processQuery(self, aQuery : SearchQuery) -> SearchQuery:
		pass

	def retrieveProducts(self, aQuery : SearchQuery) -> List:
		pass

	def rankResults(self, aProducts : List, aQuery : SearchQuery) -> List:
		pass

	def upload(self, aContent, aFilename, aContentType) -> str:
		pass

	def crop(self, aReference : str, aBox : List) -> str:
		pass

	def catalog(self) -> List:
		pass

	def getProduct(self, aProductId : int, aCustomerId : int) -> Product:
		pass

