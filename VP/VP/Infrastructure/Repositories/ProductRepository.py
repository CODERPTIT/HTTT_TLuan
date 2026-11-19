#!/usr/bin/python
# -*- coding: UTF-8 -*-
import Product
from Application.service.Ports import ProductRepositoryPort
from typing import List

class ProductRepository(ProductRepositoryPort):
	def findById(self, aProductId : int) -> Product:
		pass

	def findRelevant(self, aQuery) -> List:
		pass

	def findByCategory(self, aCategoryId : int) -> List:
		pass

	def findEligibleProducts(self) -> List:
		pass

	def save(self, aProduct : Product) -> None:
		pass

	def update(self, aProduct : Product) -> None:
		pass

	def updateStock(self, aProduct : Product) -> None:
		pass

	def saveImage(self, aContent, aFilename, aContentType) -> str:
		pass

	def cropImage(self, aReference : str, aBox) -> str:
		pass

	def imagePath(self, aReference : str) -> Path:
		pass

	def indexVector(self, aProductId : int, aVector) -> None:
		pass

	def searchVectors(self, aVector) -> List:
		pass

