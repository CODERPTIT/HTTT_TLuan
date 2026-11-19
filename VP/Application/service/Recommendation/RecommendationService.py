#!/usr/bin/python
# -*- coding: UTF-8 -*-
import Product
from typing import List

class RecommendationService(object):
	def recommend(self, aCustomerId : int, aProductId : int) -> List:
		pass

	def generateCandidates(self, aProductId : int) -> List:
		pass

	def getInteractionHistory(self, aCustomerId : int) -> List:
		pass

	def calculateContentScore(self, aSource : Product, aCandidate : Product) -> Decimal:
		pass

	def calculateCollaborativeScore(self, aViewedProductId : int, aCandidate : Product) -> Decimal:
		pass

	def calculateHybridScore(self, aContentScore : Decimal, aCollaborativeScore : Decimal) -> Decimal:
		pass

	def filterEligibleProducts(self, aProducts : List, aViewedProductId : int) -> List:
		pass

	def rankCandidates(self, aCandidates : List) -> List:
		pass

