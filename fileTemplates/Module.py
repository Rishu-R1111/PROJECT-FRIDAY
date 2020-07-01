#!/usr/bin/env python
# -*- coding: utf-8 -*-

import commons
import json
import logging
import managers.Managers 			as managers
from modules.Module 				import Module


class Base(Module):

	NAME = 'Alice'

	def __init__(self, mqttServer):
		self._logger 			= logging.getLogger('ProjectAlice')
		self._MODULE_NAME 		= self.NAME
		self._SUPPORTED_INTENTS	= []

		super(Base, self).__init__(mqttServer, self._MODULE_NAME, self._SUPPORTED_INTENTS)

	def onMessage(self, intent, message):
		if not self.filterIntent(intent, message):
			return False

		siteId 		= commons.parseSiteId(message)
		slots 		= commons.parseSlots(message)
		sessionId 	= commons.parseSessionId(message)
		customData 	= commons.parseCustomData(message)
		payload 	= json.loads(message.payload)

		return True