#!/usr/bin/python
# -*- coding: UTF-8 -*-
import Product
from typing import List

class CollaborativeRecommender(object):
	def score(self, aSourceProductId : int, aCandidate : Product) -> Decimal:
		pass

	def scores(self, aSourceProductId : int, aCandidates : List):
		pass

