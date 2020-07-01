from typing import Optional

import RPi.GPIO as GPIO

from core.ProjectAliceExceptions import SkillStartingFailed
from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class PrinterControl(AliceSkill):
	"""
	Author: mjlill
	Description: Press an imaginary button on or off
	"""

	def __init__(self):
		super().__init__()
		self._gpioPin: Optional[int] = None


	def onStart(self):
		super().onStart()

		gpioPin = self.getConfig('gpioPin')
		if gpioPin:
			self._gpioPin = int(gpioPin)
		else:
			raise SkillStartingFailed(skillName=self.name, error='Failed fetching gpio pin definition')

		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(self._gpioPin, GPIO.OUT)
		GPIO.output(self._gpioPin, GPIO.LOW)


	@IntentHandler('DoSetPrinterOn')
	def buttonOnIntent(self, session: DialogSession, **_kwargs):
		GPIO.output(self._gpioPin, GPIO.HIGH)
		self.endDialog(session.sessionId, self.TalkManager.randomTalk('DoPrinterOn'))

	@IntentHandler('DoSetPrinterOff')
	def buttonOffIntent(self, session: DialogSession, **_kwargs):
		GPIO.output(self._gpioPin, GPIO.LOW)
		self.endDialog(session.sessionId, self.TalkManager.randomTalk('DoPrinterOff'))



