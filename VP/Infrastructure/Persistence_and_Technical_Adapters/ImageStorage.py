#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import List

class ImageStorage(object):
	def save(self, aContent, aFilename, aContentType) -> str:
		pass

	def resolve(self, aReference : str) -> Path:
		pass

	def crop(self, aReference : str, aBox) -> str:
		pass

