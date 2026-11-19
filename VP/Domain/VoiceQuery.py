#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Domain import SearchQuery
from typing import List

class VoiceQuery(SearchQuery):
	def audioReference(self) -> str:
		pass

	def transcribedText(self) -> str:
		pass

