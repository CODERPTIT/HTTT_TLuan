#!/usr/bin/python
# -*- coding: UTF-8 -*-
import SearchQuery
import Product
from typing import List

class SearchController(object):
	def search(self, aQuery : SearchQuery) -> List:
		pass

	def text(self, aText : str) -> List:
		pass

	def voice(self, aTranscript : str) -> List:
		pass

	def image(self, aContent, aFilename, aContentType, aQueryText, aCropBox):
		pass

	def uploadImage(self, aContent, aFilename, aContentType, aCropBox) -> str:
		pass

	def catalog(self) -> List:
		pass

	def product(self, aProductId : int, aCustomerId : int) -> Product:
		pass

