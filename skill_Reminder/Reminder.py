import time
from datetime import datetime, timedelta
from core.base.model.AliceSkill import AliceSkill
from core.base.model.Intent import Intent
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class Reminder(AliceSkill):
	"""
	Author: Lazza. This skill utilises these main methods for functional operation
		- addReminder initiates the reminder process between user and Alice
		- Then passes onto processTheSpecifiedTime() for processing of the time
		- then onto maincode() for finalising the timer
			Amongst that process there are methods for converting spoken times to epoch and back to human time
			and Various other functions and checks, delete, how long left, etc
			Also one main Method which allows switching between the three events (Reminder/Timer/Alarm) is the
		- setEventType() method. This allows the skill to determine what of the 3 events we are dealing with
	"""
	INTERNAL_ID = 'internalId TEXT NOT NULL'
	DB_MESSAGE = 'message TEXT NOT NULL'
	DB_TIMESTAMP = 'timestamp INTEGER NOT NULL'
	DB_SITE_ID = 'SiteID TEXT NOT NULL'
	DB_EVENT_TYPE = 'EventType TEXT NOT NULL'

	_REMINDERDBNAME = 'MyReminders'
	_TIMERDBNAME = 'MyTimer'
	_ALARMDBNAME = 'MyAlarm'
	_DATABASE = {
		_REMINDERDBNAME: [
			INTERNAL_ID,
			DB_MESSAGE,
			DB_TIMESTAMP,
			DB_SITE_ID,
			DB_EVENT_TYPE
		],
		_TIMERDBNAME   : [
			INTERNAL_ID,
			DB_MESSAGE,
			DB_TIMESTAMP,
			DB_SITE_ID,
			DB_EVENT_TYPE
		],
		_ALARMDBNAME   : [
			INTERNAL_ID,
			DB_MESSAGE,
			DB_TIMESTAMP,
			DB_SITE_ID,
			DB_EVENT_TYPE
		]
	}
	_INTENT_ADD_REMINDER = Intent('ReminderEvent')
	_INTENT_ADD_DATE = Intent('ReminderTime', isProtected=True)
	_INTENT_ANSWER_YES_OR_NO = Intent('AnswerYesOrNo', isProtected=True)
	_INTENT_TIME_REMAINING = Intent('ReminderRemaining', isProtected=True)
	_INTENT_SELECT_ITEM = Intent('ChooseListItem', isProtected=True)
	_INTENT_DELETE_REMINDER = Intent('ReminderDelete', isProtected=True)
	_INTENT_USER_RANDOM_ANSWER = Intent('UserRandomAnswer', isProtected=True)


	def __init__(self):

		self._spokenDuration = ''
		self._dateTimeStr = ''
		self._dateTimeObject = ''
		self._secondsDuration = ''
		self._reminderMessage = ''
		self._dbId = 0
		self._theSiteId = self.getAliceConfig('deviceName')
		self._dbTableValues = list()
		self._selectedMessages = None
		self._dbTimeStampList = list()
		self._dbMessageList = list()
		self._dbRowIdList = list()
		self._dbSiteList = list()
		self._eventType = list()
		self._activeDataBase = 'MyReminders'
		self._dataBaseList = ['MyReminders', 'MyTimer', 'MyAlarm']
		self._TimerEventType = list()

		self._INTENTS = [
			self._INTENT_ANSWER_YES_OR_NO,
			self._INTENT_ADD_DATE,
			self._INTENT_SELECT_ITEM,
			self._INTENT_USER_RANDOM_ANSWER,
			(self._INTENT_ADD_REMINDER, self.addReminder)
		]

		# init Dialog mapping to prevent dialog clashing with other skills
		self._INTENT_ANSWER_YES_OR_NO.dialogMapping = {
			'ConfirmIfDeletingAllMessages': self.actionFromYesNoAnswer,
			# 'ConfirmIfMessageAndTimeCorrect': self.processTheSpecifiedTime

		}

		self._INTENT_ADD_REMINDER.dialogMapping = {
			'AddMessageToReminder': self.processTheSpecifiedTime
		}

		self._INTENT_USER_RANDOM_ANSWER.dialogMapping = {
			'AddMessageToReminder': self.processTheSpecifiedTime
		}

		self._INTENT_DELETE_REMINDER.dialogMapping = {
			'DeleteSomeReminder': self.deleteRequestedReminder
		}

		self._INTENT_SELECT_ITEM.dialogMapping = {
			'SelectedItemFromList': self.extractRequestedItemFromList,
			'askWhatItemFromList' : self.extractRequestedItemFromList
		}

		super().__init__(self._INTENTS, databaseSchema=self._DATABASE)


	# Cleanup the Db on boot up
	def onStart(self):
		super().onStart()
		self.logInfo(f'Doing database maintenance')
		self.cleanupDeadTimers()
		self.onFiveMinute()


	def runShortTimer(self, event: str):
		self.reminderSound(event)
		self.ThreadManager.doLater(
			interval=0.5,
			func=self.say(
				text='Your short timer has finished'
			),
		)


	# This is called directly by the mapping for intents because DURATION was specified
	def addReminder(self, session: DialogSession):
		self.setEventType(session)
		# if user set a short time do this
		if 'ShortTimer' in session.slots and 'Duration' in session.slots:
			self._secondsDuration = self.Commons.getDuration(session)
			self._reminderMessage = 'for the timer with no topic'

			self.ThreadManager.doLater(
				interval=self._secondsDuration,
				func=self.runShortTimer,
				args=[self._eventType]
			)
			self.endDialog(
				sessionId=session.sessionId,
				text=f'ok, done'
			)
			return

		# If theres no reminder date or duration specified then ask for a message
		if f'{self._eventType}DateAndTime' in session.slots or 'Duration' in session.slots:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(text='respondReminderMessage', replace=[self._eventType]),
				intentFilter=[self._INTENT_USER_RANDOM_ANSWER],
				currentDialogState='AddMessageToReminder'
			)

		else:
			if f'{self._eventType}DateAndTime' not in session.slots or 'Duration' not in session.slots:
				self.continueDialog(
					sessionId=session.sessionId,
					text=self.randomTalk(text='respondSetDuration', replace=[self._eventType]),
					intentFilter=[self._INTENT_ADD_DATE],
					currentDialogState='AddedTheDateOrDuration',
					slot='ReminderDateAndTime'
				)


	def processTheSpecifiedTime(self, session: DialogSession):
		if f'{self._eventType}DateAndTime' in session.slotsAsObjects:

			self._spokenDuration = session.slotValue(f'{self._eventType}DateAndTime').split()  # returns format [2020-04-08, 10:25:00, +10]
			del self._spokenDuration[-1]  # Removes the timezone off the end
			self._dateTimeStr = ' '.join(self._spokenDuration)  # converts the list to a string
			self._dateTimeObject = datetime.strptime(self._dateTimeStr, '%Y-%m-%d %H:%M:%S')
			self._secondsDuration = self._dateTimeObject - datetime.today()  # find the difference between requested time and now

		if 'Duration' in session.slotsAsObjects:
			self._secondsDuration = self.Commons.getDuration(session)  # Gets the requested duration in seconds

		self._reminderMessage = session.payload['input']  # set the reminder message

		if f'{self._eventType}DateAndTime' in session.slotsAsObjects:  # Convert to Seconds if its called with DateAndTime slot
			secs = round(self._secondsDuration.total_seconds())
		else:
			secs = self._secondsDuration  # Seconds are already converted so set the secs var

		if 'Food' in session.slots:
			self.setFoodTimer(session, secs)

		else:
			self.processAndStoreReminder(session, secs)


	# This does the actual setting of the timer details and storing to Db
	def processAndStoreReminder(self, session: DialogSession, secs: int):

		self.logDebug(f'The requested time converted to seconds is {secs}')

		# count of the amount of rows in the Database
		myTablecount = self.tableRowCount()

		# Convert to Epoch timestamp in Seconds for storing in Db
		timeStampForDb = self.createEpochTimeStamp(secs)

		# VocalSeconds is used to give Alice's reply a human friendly response
		vocalSeconds = str(timedelta(seconds=secs))

		# TODO unhardcode language
		hour, minute, second = vocalSeconds.split(':')
		vocalTime = ''

		try:
			hours = int(hour)
			minutes = int(minute)
			seconds = int(second)
		except ValueError:
			self.logWarning('Something went wrong decoding time')
			hours = 0
			minutes = 0
			seconds = 60

		if seconds > 0:
			vocalTime = f'{seconds} seconds'
		if minutes > 0:
			if minutes > 1:
				if seconds > 0:
					vocalTime = f'{minutes} minutes and {vocalTime}'
				else:
					vocalTime = f'{minutes} minutes'
			else:
				if seconds > 0:
					vocalTime = f'{minutes} minute and {vocalTime}'
				else:
					vocalTime = f'{minutes} minute'
		if hours > 0:
			if hours > 1:
				vocalTime = f'{hours} hours, {vocalTime}'
			else:
				vocalTime = f'{hours} hour and {vocalTime}'


		# Set event type for later recall from db when dofiveMinute is called after a reboot
		self._TimerEventType = self._eventType

		if secs < 299:
			self.ThreadManager.doLater(
				interval=secs,
				func=self.runReminder,
				args=[self._eventType, self._reminderMessage]
			)

		# Alice Confirming that the Reminder has been set ..........................................................
		self.endDialog(
			sessionId=session.sessionId,
			text=self.randomTalk('respondConfirmed', replace=[self._eventType, self._reminderMessage, vocalTime])
		)

		# write Timer info to the database or not depending on length of time (saves double up reminder from onFive trigger
		try:
			if secs >= 299:
				self.databaseInsert(
					tableName=self._activeDataBase,
					values={'internalID': myTablecount + 1, 'message': self._reminderMessage, 'timestamp': timeStampForDb, 'SiteID': self._theSiteId, 'EventType': self._eventType}
				)
		except:
			self.logError(f'Failed to enable timer due to **Database** temporarily being locked')


	# Respond with The Reminder once time is finished,
	def runReminder(self, event: str, savedMessage: str):
		self.reminderSound(event)
		self.ThreadManager.doLater(interval=0.5, func=self.say, kwargs={'text': self.randomTalk(text='respondReminder', replace=[event, savedMessage]), 'siteId': self._theSiteId})


	def foodReminder(self):
		self.say(self.randomTalk(text='respondFoodTimer'), siteId=self._theSiteId)


	# required
	@staticmethod
	def createEpochTimeStamp(seconds: int) -> int:
		timeStampForDatabase = datetime.now() + timedelta(seconds=seconds)
		dateTime = str(timeStampForDatabase)
		pattern = '%Y-%m-%d %H:%M:%S.%f'
		epoch = int(time.mktime(time.strptime(dateTime, pattern)))
		return epoch


	# sets a mid timer, timer to alert to go check the food
	def setFoodTimer(self, session: DialogSession, secs):
		checkTheFoodTimer = secs / 2
		self.ThreadManager.doLater(
			interval=checkTheFoodTimer,
			func=self.foodReminder
		)
		self.processAndStoreReminder(session, secs)


	def askIfTheDetailsAreCorrect(self, session: DialogSession):

		if 'ReminderDeleteAll' in session.slots:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('respondAskConfirmation', replace=[self._eventType]),
				intentFilter=[self._INTENT_ANSWER_YES_OR_NO],
				currentDialogState='ConfirmIfDeletingAllMessages',
				probabilityThreshold=0.1
			)


	# do something in responce to a yes or no reply
	def actionFromYesNoAnswer(self, session: DialogSession):

		if 'ConfirmIfDeletingAllMessages' in session.currentState:

			if self.Commons.isYes(session):
				self.deleteRequestedReminder(session)
			else:
				self.endDialog(
					sessionId=session.sessionId,
					text=self.randomTalk('respondToANoReply', replace=[self._eventType]),
				)


	# This returns the amount of rows in the database table
	def tableRowCount(self) -> int:
		dbRows = self.databaseFetch(
					tableName=self._activeDataBase,
					query='SELECT COUNT (*) FROM :__table__',
					method='all'
				)
		return dbRows[0]


	# This updates the internalID value to match table rowid
	def updateInternalIdNumberOfDb(self):
		i = 0
		while i <= len(self._dataBaseList) - 1:
			if i == 0:
				self._eventType = 'Reminder'
				self._activeDataBase = self._REMINDERDBNAME
			elif i == 1:
				self._eventType = 'Timer'
				self._activeDataBase = self._TIMERDBNAME
			else:
				self._eventType = 'Alarm'
				self._activeDataBase = self._ALARMDBNAME
			self.viewTableValues()

			try:
				# noinspection SqlResolve
				self.DatabaseManager.update(
					tableName=self._activeDataBase,
					callerName=self.name,
					query='UPDATE :__table__ SET internalId = rowid'
				)
			except:
				self.ThreadManager.doLater(
					interval=300,
					func=self.updateInternalIdNumberOfDb()
				)
			i += 1


	# This sets "self._dbTableValues" to a list of all current Database table values
	def viewTableValues(self):
		# self.updateInternalIdNumberOfDb()  # resets internalId column to rowid value

		# Todo What??
		dbTableList = []
		for row in self.databaseFetch(
				tableName=self._activeDataBase,
				query='SELECT * FROM :__table__ ',
				method='all'
		):

			if tuple(row):
				dbTableList.append(tuple(row))

		self._dbTableValues = dbTableList  # Get the entire Reminder Database table
		self._dbSiteList = [x[3] for x in self._dbTableValues]  # get list of SiteId for use on a Alice restart
		self._dbTimeStampList = [x[2] for x in self._dbTableValues]  # get list of TimeStamps
		self._dbMessageList = [x[1] for x in self._dbTableValues]  # get the list of messages
		self._dbRowIdList = [x[0] for x in self._dbTableValues]  # get The list of row ID's
		self._TimerEventType = [x[4] for x in self._dbTableValues]  # get event type from db
		self.cleanupDeadTimers()


	# Returns the remaining time left on a choosen timer
	def getTimeRemaining(self, session: DialogSession):
		convertedTime = self.convertEpochMinusNowToHumanReadableTime()

		self.endDialog(
			sessionId=session.sessionId,
			text=self.randomTalk('respondTimeRemaining', replace=[convertedTime, self._eventType]),
			siteId=session.siteId
		)


	# This starts the process of asking user what item to look up in the list
	def getItemFromList(self, session: DialogSession):
		completeMessageString = ''

		i = 0
		# Reads a list of items and adds it to one string
		for x in self._dbMessageList:
			i += 1
			commonString = f'The {self._eventType} number {i} <break time=\"250ms\"/>.'
			completeMessageString = f'{completeMessageString} {commonString} {x} <break time=\"250ms\"/>,'

		if len(self._dbMessageList) == 0:
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('respondNoActive', replace=[self._eventType])
			)

		elif len(self._dbMessageList) == 1:
			self._selectedMessages = self._dbMessageList[0]

			if 'ReminderDeleteAll' in session.slotsAsObjects or 'ReminderDelete' in session.slotsAsObjects:
				self.deleteRequestedReminder(session)

			elif f'{self._eventType}RemainingTime' in session.slotsAsObjects:
				self.getTimeRemaining(session)

			elif f'{self._eventType}Stop' in session.slotsAsObjects:
				self.userAskedToStopReminder(session)

			else:
				return
		else:
			self.askForWhichItems(session, self._dbMessageList, completeMessageString)


	# This is used for asking the user to select the item from a list and return it to extractRequestedItemFromList()
	def askForWhichItems(self, session: DialogSession, dbMessageList: list, completeMessageString: str):
		dbMessageList.insert(0, self._eventType)

		self.continueDialog(
			sessionId=session.sessionId,
			text=self.randomTalk('respondListOfItems', replace=[completeMessageString]),  # replace=[message for message in self._dbMessageList]),
			intentFilter=[self._INTENT_SELECT_ITEM],
			currentDialogState='askWhatItemFromList',
			probabilityThreshold=0.1,
			slot='Number'
		)
		del dbMessageList[0]


	# This currently returns the selected number to extractRequestedItemFromList()
	def extractRequestedItemFromList(self, session: DialogSession):
		intent = session.intentName

		if intent == self._INTENT_SELECT_ITEM:
			if 'Number' in session.slotsAsObjects:

				if session.slotValue('Number') > len(self._dbMessageList):
					self.logWarning(f'That number appears to be invalid')
					self.getItemFromList(session)
					return

				itemChosen = session.slotValue('Number')
				itemChosen = int(itemChosen) - 1  # turn float into a int then subtract 1 for indexing the list
				self._selectedMessages = self._dbMessageList[itemChosen]  # extract the actual requested message

				if 'ReminderDelete' in session.slotsAsObjects:
					self.deleteRequestedReminder(session)

				elif f'{self._eventType}RemainingTime' in session.slotsAsObjects:
					self.getTimeRemaining(session)

				elif f'{self._eventType}Stop' in session.slotsAsObjects:
					self.userAskedToStopReminder(session)

			else:
				self.continueDialog(
					sessionId=session.sessionId,
					text='respondNoNumber',
					intentFilter=[self._INTENT_SELECT_ITEM],
					currentDialogState='askWhatItemFromList'
				)
		else:
			self.logWarning(f'The expected Intent was not received')


	def cleanupDeadTimers(self):

		i = 0

		for x in self._dbTimeStampList:  # x = a individual timestamp from _dbTimeStampList

			epochTimeNow = datetime.now().timestamp()  # Returns the epoch time for right now

			if x < epochTimeNow:

				# noinspection SqlResolve
				self.DatabaseManager.delete(
					tableName=self._activeDataBase,
					query='DELETE FROM :__table__ WHERE timestamp <= :tmpTimestamp',
					values={'tmpTimestamp': epochTimeNow},
					callerName=self.name
				)
				i += 1

		if i > 0:
			self.viewTableValues()
			self.logDebug(f'Just deleted {i} redundant event/s from {self._activeDataBase}')


	# This stops a current timer on request
	def userAskedToStopReminder(self, session: DialogSession):
		self.setEventType(session)

		# noinspection SqlResolve
		self.DatabaseManager.delete(
			tableName=self._activeDataBase,
			query='DELETE FROM :__table__ WHERE message = :tmpMessage',
			values={'tmpMessage': self._selectedMessages},
			callerName=self.name)

		self.endDialog(
			sessionId=session.sessionId,
			text=self.randomTalk('respondDelete', replace=[self._eventType]),
			siteId=session.siteId
		)
		self.cleanupDeadTimers()


	# Used to Convert the Database Timestamp into seconds
	def convertEpochMinusNowToSeconds(self, epochSeconds: int = None) -> float:
		epochTimeNow = datetime.now().timestamp()  # Returns the epoch time for right now
		indexPos = 0
		i = 0

		if epochSeconds is not None:
			epoch2Seconds = (epochSeconds - epochTimeNow)
			return epoch2Seconds
		else:
			length = len(self._dbTableValues)
			while i < length:

				if self._selectedMessages in self._dbTableValues[i]:
					indexPos = i
					break
				i += 1

			timestampActual = self._dbTableValues[indexPos][2]
			differenceInSeconds = (timestampActual - epochTimeNow)

			return differenceInSeconds


	# Converts Epoch time from DB to a Human readable output
	def convertEpochMinusNowToHumanReadableTime(self) -> str:
		convertedToSeconds = self.convertEpochMinusNowToSeconds()

		return str(timedelta(seconds=round(convertedToSeconds)))


	# This deletes a Item from DB the cleans up the row id's
	def deleteRequestedReminder(self, session: DialogSession):
		self.setEventType(session)

		if 'ReminderDeleteAll' not in session.slots:
			# noinspection SqlResolve
			self.DatabaseManager.delete(
				tableName=self._activeDataBase,
				query='DELETE FROM :__table__ WHERE message = :tmpMessage',
				values={'tmpMessage': self._selectedMessages},
				callerName=self.name)

			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('respondDelete', replace=[self._eventType]),
				siteId=session.siteId,
			)

			self.logInfo(f'Successfully deleted the requested {self._eventType} from the database')
			return
		else:
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('respondDeleteAll', replace=[self._eventType]),
				siteId=session.siteId,
			)
			# noinspection SqlWithoutWhere
			self.DatabaseManager.delete(
				tableName=self._activeDataBase,
				query='DELETE FROM :__table__ ',
				callerName=self.name
			)
		self.cleanupDeadTimers()


	# This does a 5 minute check of the stored timers and if a timer is within 320 seconds of activating
	# then we initiate the actual timer thread
	def onFiveMinute(self):
		self.viewTableValues()

		i = 0

		while i <= len(self._dataBaseList) - 1:
			self._activeDataBase = self._dataBaseList[i]
			if 'MyReminder' in self._activeDataBase:
				self._eventType = 'Reminder'
			elif 'MyTimer' in self._activeDataBase:
				self._eventType = 'Timer'
			else:
				self._eventType = 'Alarm'

			self.viewTableValues()
			self.logDebug(f'Checking for active timers in {self._activeDataBase} database')

			for x in self._dbTableValues:
				timerMessage = x[1]
				self._TimerEventType = x[4]
				theSeconds = x[2]
				convertedTime = self.convertEpochMinusNowToSeconds(theSeconds)
				float(convertedTime)
				vocalSeconds = str(timedelta(seconds=round(convertedTime)))
				self.logDebug(f'You have a {self._TimerEventType} with {vocalSeconds} left on it')
				cleanUpSeconds = convertedTime + 20.0

				if convertedTime < 299.0:
					self.ThreadManager.doLater(
						interval=convertedTime,
						func=self.runReminder,
						args=[self._TimerEventType, timerMessage]
					)
					self.ThreadManager.doLater(
						interval=cleanUpSeconds,
						func=self.viewTableValues()
					)
			i += 1


	def reminderSound(self, event: str):

		path = event
		if 'Reminder' in event:
			soundFile = 'Reminder.wav'
		elif 'Timer' in event:
			soundFile = 'Timer.wav'
		else:
			soundFile = 'Alarm.wav'

		self.playSound(
			soundFilename=soundFile,
			location=self.getResource(f'Sounds/{path}'),
			sessionId='ReminderTriggered',
			siteId=self._theSiteId
		)


	# Critical method for allowing reminder/timer/alarm to all play nicely together
	def setEventType(self, session: DialogSession):
		self._theSiteId = session.siteId

		if 'ReminderEvent' in session.slots or 'ReminderSlot' in session.slots or 'ReminderStop' in session.slots:
			self._eventType = 'Reminder'
			self._activeDataBase = self._REMINDERDBNAME
		elif 'TimerEvent' in session.slots or 'TimerSlot' in session.slots or 'TimerStop' in session.slots:
			self._eventType = 'Timer'
			self._activeDataBase = self._TIMERDBNAME
		else:
			self._eventType = 'Alarm'
			self._activeDataBase = self._ALARMDBNAME

		self.viewTableValues()


	# Used for setting up a alarm - required
	@IntentHandler('SetUpAlarm')
	def setAlarmIntent(self, session: DialogSession):
		self.addReminder(session)


	# Used for setting up a timer - required
	@IntentHandler('SetUpTimer')
	def setTimerIntent(self, session: DialogSession):
		self.addReminder(session)


	# Used for deleting a item(s) - required
	@IntentHandler('ReminderDelete')
	def deleteRemindersIntent(self, session: DialogSession):
		self.setEventType(session)

		if 'ReminderDeleteAll' in session.slots:
			self.askIfTheDetailsAreCorrect(session)
		else:
			self.getItemFromList(session)


	# Used for when user asks how long left on timer - required
	@IntentHandler('ReminderRemaining')
	def remainingTimeReminderIntent(self, session: DialogSession):
		self.setEventType(session)

		if 'ReminderSlot' in session.slots or 'TimerSlot' in session.slots or 'AlarmSlot' in session.slots:
			self.getItemFromList(session)


	# Used for stopping a event - required
	@IntentHandler('ReminderStop')
	def stopReminderIntent(self, session: DialogSession):
		self.setEventType(session)
		self.getItemFromList(session)


	@IntentHandler('ReminderTime')
	def addRemiderIntent(self, session: DialogSession):
		"""
		this method is likely to be removed in the near future. No need for it
		:param session:
		:return:
		"""
		pass


	@IntentHandler('ReminderMessage')
	def addReminderIntent(self, session: DialogSession):
		self.processTheSpecifiedTime(session)
