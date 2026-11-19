#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
import Product
import SearchQuery
from typing import List

class ProductRepositoryPort(object):
	"""@Interface"""
	__metaclass__ = ABCMeta
	@abstractmethod
	def findById(self, aProductId : int) -> Product:
		pass

	@abstractmethod
	def findRelevant(self, aQuery : SearchQuery) -> List:
		pass

	@abstractmethod
	def findEligibleProducts(self) -> List:
		pass

	@abstractmethod
	def updateStock(self, aProduct : Product) -> None:
		pass

	@abstractmethod
	def saveImage(self, aContent, aFilename, aContentType) -> str:
		pass

	@abstractmethod
	def cropImage(self, aReference : str, aBox : List) -> str:
		pass

	@abstractmethod
	def imagePath(self, aReference : str) -> Path:
		pass

	@abstractmethod
	def indexVector(self, aProductId : int, aVector : List) -> None:
		pass

	@abstractmethod
	def searchVectors(self, aVector : List) -> List:
		pass

