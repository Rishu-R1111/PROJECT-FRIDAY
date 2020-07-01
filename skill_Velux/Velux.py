import threading

from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler, MqttHandler


class Velux(AliceSkill):
	"""
	Author: Psychokiller1888
	Description: Control your velux equipment with your voice! This requires a velux remote hack
	"""

	def __init__(self):
		super().__init__()
		self._waiting = threading.Event()


	@MqttHandler('projectalice/devices/velux/state')
	def veluxState(self, session: DialogSession):
		if session.payload.get('state', '') == 1:
			self._waiting.clear()
		elif not self._waiting.is_set():
			self._waiting.set()


	@IntentHandler('Velux_DoAction')
	def handleVelux(self, session: DialogSession, **_kwargs):
		if self._waiting.is_set():
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(text='willDoLater')
			)
		else:
			location = session.slotValue(slotName='Location', defaultValue=session.siteId)
			action = session.slotValue(slotName='Action', defaultValue='open')
			device = session.slotValue(slotName='Device', defaultValue='windows')
			duration = session.slotValue(slotName='Duration', defaultValue=-1)
			percentage = session.slotValue(slotName='Percentage', defaultValue=100)

			self.publish(
				topic=f'projectalice/devices/{device}/{action}',
				payload = {
					'location'  : location,
					'duration'  : duration,
					'percentage': percentage
				}
			)

			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(text=f'ok', replace=[])
			)
