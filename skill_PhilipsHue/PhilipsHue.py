import time

from core.ProjectAliceExceptions import SkillStartDelayed, SkillStartingFailed
from core.base.model.AliceSkill import AliceSkill
from core.base.model.Intent import Intent
from core.commons import constants
from core.dialog.model.DialogSession import DialogSession
from .models.PhueAPI import Bridge, LinkButtonNotPressed, NoPhueIP, NoSuchGroup, NoSuchLight, NoSuchScene, NoSuchSceneInGroup, PhueRegistrationError, UnauthorizedUser


class PhilipsHue(AliceSkill):

	_INTENT_LIGHT_ON = Intent('PowerOnLights')
	_INTENT_LIGHT_OFF = Intent('PowerOffLights')
	_INTENT_LIGHT_SCENE = Intent('SetLightsScene')
	_INTENT_MANAGE_LIGHTS = Intent('ManageLights')
	_INTENT_DIM_LIGHTS = Intent('DimLights')
	_INTENT_ANSWER_PERCENT = Intent('AnswerPercent', isProtected=True)
	_INTENT_USER_ANSWER = Intent('UserRandomAnswer', isProtected=True)


	def __init__(self):
		self._INTENTS = [
			(self._INTENT_LIGHT_ON, self.lightOnIntent),
			(self._INTENT_LIGHT_OFF, self.lightOffIntent),
			(self._INTENT_LIGHT_SCENE, self.lightSceneIntent),
			(self._INTENT_MANAGE_LIGHTS, self.manageLightsIntent),
			(self._INTENT_DIM_LIGHTS, self.dimLightsIntent),
			self._INTENT_ANSWER_PERCENT,
			self._INTENT_USER_ANSWER
		]

		self._INTENT_ANSWER_PERCENT.dialogMapping = {
			'whatPercentage': self.dimLightsIntent
		}

		self._INTENT_USER_ANSWER.dialogMapping = {
			'whatScenery': self.lightSceneIntent
		}

		# noinspection PyTypeChecker
		self._bridge: Bridge = None
		self._bridgeConnectTries = 0
		self._stateBackup = dict()

		super().__init__(self._INTENTS)

		self._hueConfigFile = self.getResource('phueAPI.conf')
		if not self._hueConfigFile.exists():
			self.logInfo('No phueAPI.conf file in PhilipsHue skill directory')


	def onStart(self):
		super().onStart()

		self._bridge = Bridge(ip=self.getConfig('phueBridgeIp'), confFile=self._hueConfigFile)

		if not self.delayed:
			try:
				if self._bridge.connect(autodiscover=not self.getAliceConfig('stayCompletlyOffline')):
					self.logInfo('Connected to Philips Hue bridge')

			except UnauthorizedUser:
				try:
					self._bridge.register()
				except LinkButtonNotPressed:
					self.logInfo('User is not authorized')
					self.delayed = True
					raise SkillStartDelayed(self.name)
			except NoPhueIP:
				raise SkillStartingFailed(skillName=self.name, error='Bridge IP not set and stay completly offline set to True, cannot auto discover Philips Hue bridge')
		else:
			if not self.ThreadManager.isThreadAlive('PHUERegister'):
				self.ThreadManager.newThread(name='PHUERegister', target=self._registerOnBridge)


	def _registerOnBridge(self):
		try:
			self._bridge.register()
			self._bridgeConnectTries = 0

			self.ThreadManager.doLater(
				interval=3,
				func=self.say,
				args=[self.randomTalk('pressBridgeButtonConfirmation')]
			)
		except LinkButtonNotPressed:
			if self._bridgeConnectTries < 3:
				self.say(text=self.randomTalk('pressBridgeButton'))
				self._bridgeConnectTries += 1
				self.logWarning('Bridge not registered, please press the bridge button, retry in 20 seconds')
				time.sleep(20)
				self._registerOnBridge()
			else:
				self.ThreadManager.doLater(interval=3, func=self.say, args=[self.randomTalk('pressBridgeButtonTimeout')])
				raise SkillStartingFailed(skillName=self.name, error=f"Couldn't reach bridge")
		except PhueRegistrationError as e:
			raise SkillStartingFailed(skillName=self.name, error=f'Error connecting to bridge: {e}')


	def onBooted(self):
		super().onBooted()
		if not self.delayed:
			self.onFullHour()


	def onSleep(self):
		self._bridge.group(0).off()


	def onFullHour(self):
		if not self.getConfig('matchLightWithDaytime'):
			return

		partOfTheDay = self.Commons.partOfTheDay().capitalize()
		if partOfTheDay not in self._bridge.scenesByName:
			return

		for group in self._bridge.groups.values():
			try:
				if group.isOn:
					group.scene(sceneName=partOfTheDay)
			except NoSuchScene:
				self.logInfo(f'Scene {partOfTheDay} not found on the bridge')
			except NoSuchSceneInGroup:
				self.logInfo(f'Scene {partOfTheDay} not found for group {group.name}, you should consider adding it')


	def _getLocations(self, session: DialogSession) -> list:
		locations = [slot.value['value'].lower() for slot in session.slotsAsObjects.get('Location', list())]
		if not locations:
			locations = [self.getAliceConfig('deviceName').lower()]

		return locations if self._validateLocations(session, locations) else list()


	def _validateLocations(self, session: DialogSession, locations: list) -> bool:
		if constants.EVERYWHERE in locations:
			return True

		for location in locations:
			if location not in self._bridge.groupsByName:
				self.endDialog(sessionId=session.sessionId, text=self.randomTalk(text='roomUnknown', replace=[location]))
				return False
		return True


	def lightOnIntent(self, session: DialogSession):
		partOfTheDay = self.Commons.partOfTheDay().capitalize()

		locations = self._getLocations(session)
		for location in locations:
			if location == constants.EVERYWHERE:
				try:
					self._bridge.group(0).scene(sceneName=partOfTheDay)
					break
				except NoSuchSceneInGroup:
					self._bridge.group(0).on()
			else:
				try:
					self._bridge.group(groupName=location).scene(sceneName=partOfTheDay)
					break
				except NoSuchSceneInGroup:
					self._bridge.group(groupName=location).on()
				except NoSuchGroup:
					self.logWarning(f'Requested group "{location}" does not exist on the Philips Hue bridge')

		if locations:
			self.endDialog(session.sessionId, text=self.randomTalk('confirm'))


	def lightOffIntent(self, session: DialogSession):
		locations = self._getLocations(session)
		for location in locations:
			if location == constants.EVERYWHERE:
				self._bridge.group(0).off()
				break

			try:
				self._bridge.group(groupName=location).off()
			except NoSuchGroup:
				self.logWarning(f'Requested group "{location}" does not exist on the Philips Hue bridge')

		if locations:
			self.endDialog(session.sessionId, text=self.randomTalk('confirm'))


	def lightSceneIntent(self, session: DialogSession):
		if len(session.slotsAsObjects.get('Scene', list())) > 1:
			self.endDialog(session.sessionId, text=self.randomTalk('cantSpecifyMoreThanOneScene'))
			return
		else:
			scene = session.slotValue('Scene').lower()

		locations = self._getLocations(session)
		if not scene:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('whatScenery'),
				intentFilter=[self._INTENT_USER_ANSWER],
				currentDialogState='whatScenery'
			)
			return
		elif scene not in self._bridge.scenesByName:
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk(text='sceneUnknown', replace=[scene]))
			return

		done = False
		for location in locations:
			try:
				self._bridge.group(groupName=location).scene(sceneName=scene)
				done = True
			except NoSuchSceneInGroup:
				self.logInfo(f'Requested scene "{scene}" for group "{location}" does not exist on the Philips Hue bridge')
			except NoSuchGroup:
				self.logWarning(f'Requested group "{location}" does not exist on the Philips Hue bridge')

		if not done:
			self.endDialog(session.sessionId, text=self.randomTalk('sceneNotInThisRoom'))
			return

		if locations:
			self.endDialog(session.sessionId, text=self.randomTalk('confirm'))


	def manageLightsIntent(self, session: DialogSession):
		partOfTheDay = self.Commons.partOfTheDay().capitalize()

		locations = self._getLocations(session)
		for location in locations:
			if location == constants.EVERYWHERE:
				group = self._bridge.group(0)
				group.off() if group.isOn else group.on()
				break

			try:
				group = self._bridge.group(groupName=location)
				if group.isOn:
					group.off()
					continue

				try:
					group.scene(sceneName=partOfTheDay)
				except (NoSuchScene, NoSuchSceneInGroup):
					group.on()

			except NoSuchGroup:
				self.logWarning(f'Requested group "{location}" does not exist on the Philips Hue bridge')
			except NoSuchLight:
				pass

		if locations:
			self.endDialog(session.sessionId, text=self.randomTalk('confirm'))


	def dimLightsIntent(self, session: DialogSession):
		if 'Percent' not in session.slots:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('whatPercentage'),
				intentFilter=[self._INTENT_ANSWER_PERCENT],
				currentDialogState='whatPercentage'
			)
			return

		percentage = self.Commons.clamp(session.slotValue('Percent'), 0, 100)
		brightness = int(round(254 / 100 * percentage))

		locations = self._getLocations(session)
		for location in locations:
			if location == constants.EVERYWHERE:
				self._bridge.group(0).brightness = brightness
				break

			try:
				self._bridge.group(groupName=location).brightness = brightness
			except NoSuchGroup:
				self.logWarning(f'Requested group "{location}" does not exist on the Philips Hue bridge')

		if locations:
			self.endDialog(session.sessionId, text=self.randomTalk('confirm'))


	def runScene(self, scene: str, group: str = None):
		try:
			if group:
				self._bridge.group(groupName=group).scene(sceneName=scene)
				return
			else:
				self._bridge.group(0).scene(sceneName=scene)
				return
		except NoSuchGroup:
			self.logWarning(f'Requested group "{group}" does not exist on the Philips Hue bridge')
		except NoSuchScene:
			self.logWarning(f'Requested scene "{scene}" does not exist on the Philips Hue bridge')


	def lightsOff(self, group: int = 0):
		self._bridge.group(group).off()
