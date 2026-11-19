#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod
from typing import List

class SearchQuery___abstract__(object):
	__metaclass__ = ABCMeta
	@classmethod
	def searchQueryId(self) -> int:
		pass

	@classmethod
	def createdAt(self) -> datetime:
		pass

