#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

class VectorIndex(object):
	def store(self, aProductId : int, aVector : List) -> None:
		pass

	def cosine(self, aLeft : List, aRight : List):
		pass

	def search(self, aVector : List, aLimit : int) -> List:
		pass

