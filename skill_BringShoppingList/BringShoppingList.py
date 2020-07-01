from typing import Tuple

from BringApi.BringApi import BringApi

from core.ProjectAliceExceptions import SkillStartingFailed
from core.base.model.Intent import Intent
from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import AnyExcept, Online, IntentHandler


class BringShoppingList(AliceSkill):
	"""
	Author: philipp2310
	Description: maintaines a Bring! shopping list
	"""

	def __init__(self):
		super().__init__()
		self._uuid = self.getConfig('uuid')
		self._uuidlist = self.getConfig('listUuid')
		self._bring = None


	def onStart(self):
		super().onStart()
		self._connectAccount()


	def bring(self):
		if not self._bring:
			if not self._uuid or not self._uuidlist:
				self._uuid, self._uuidlist = BringApi.login(self.getConfig('bringEmail'), self.getConfig('bringPassword'))
				self.updateConfig('uuid', self._uuid)
				self.updateConfig('listUuid', self._uuidlist)

			self._bring = BringApi(self._uuid, self._uuidlist)
		return self._bring


	@Online
	def _connectAccount(self):
		try:
			self._bring = self.bring()
		except BringApi.AuthentificationFailed:
			raise SkillStartingFailed(skillName=self._name, error='Please check your account login and password')


	def _deleteCompleteList(self):
		"""
		perform the deletion of the complete list
		-> load all and delete item by item
		"""
		items = self.bring().get_items()['purchase']
		for item in items:
			self.bring().recent_item(item['name'])


	def _addItemInt(self, items) -> Tuple[list, list]:
		"""
		internal method to add a list of items to the shopping list
		:returns: two splitted lists of successful adds and items that already existed.
		"""
		bringItems = self.bring().get_items(self.LanguageManager.activeLanguageAndCountryCode)['purchase']
		added = list()
		exist = list()
		for item in items:
			if not any(entr['name'].lower() == item.lower() for entr in bringItems):
				self.bring().purchase_item(BringApi.translateToCH(item, self.LanguageManager.activeLanguageAndCountryCode), "")
				added.append(item)
			else:
				exist.append(item)
		return added, exist


	def _deleteItemInt(self, items: list) -> Tuple[list, list]:
		"""
		internal method to delete a list of items from the shopping list
		:returns: two splitted lists of successful deletions and items that were not on the list
		"""
		bringItems = self.bring().get_items(self.LanguageManager.activeLanguageAndCountryCode)['purchase']
		removed = list()
		exist = list()
		for item in items:
			for entr in bringItems:
				if entr['name'].lower() == item.lower():
					self.bring().recent_item(BringApi.translateToCH(entr['name'], self.LanguageManager.activeLanguageAndCountryCode))
					removed.append(item)
					break
			else:
				exist.append(item)
		return removed, exist


	def _checkListInt(self, items: list) -> Tuple[list, list]:
		"""
		internal method to check if a list of items is on the shopping list
		:returns: two splitted lists, one with the items on the list, one with the missing ones
		"""
		bringItems = self.bring().get_items(self.LanguageManager.activeLanguageAndCountryCode)['purchase']
		found = list()
		missing = list()
		for item in items:
			if any(entr['name'].lower() == item.lower() for entr in bringItems):
				found.append(item)
			else:
				missing.append(item)
		return found, missing


	def _getShopItems(self, answer: str, session: DialogSession) -> list:
		"""get the values of shopItem as a list of strings"""
		intent = session.intentName
		if intent == Intent('SpellWord'):
			item = ''.join([slot.value['value'] for slot in session.slotsAsObjects['Letters']])
			return [item.capitalize()]

		items = [x.value['value'] for x in session.slotsAsObjects.get('shopItem', list()) if x.value['value'] != "unknownword"]

		if not items:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(f'{answer}_what'),
				intentFilter=[Intent('whatItem_bringshop'), Intent('SpellWord')],
				currentDialogState=intent.split(':')[-1])
		return items


	### INTENTS ###
	@IntentHandler('Bring_deleteList')
	@Online
	def delListIntent(self, session: DialogSession):
		self.continueDialog(
			sessionId=session.sessionId,
			text=self.randomTalk('chk_del_all'),
			intentFilter=[Intent('AnswerYesOrNo')],
			currentDialogState='confDelList_Bring')


	@AnyExcept(exceptions=BringApi.AuthentificationFailed, text='authFailed')
	@Online
	@IntentHandler('AnswerYesOrNo', requiredState='confDelList_Bring', isProtected=True)
	def confDelIntent(self, session: DialogSession):
		if self.Commons.isYes(session):
			self._deleteCompleteList()
			self.endDialog(session.sessionId, text=self.randomTalk('del_all'))
		else:
			self.endDialog(session.sessionId, text=self.randomTalk('nodel_all'))


	@AnyExcept(exceptions=BringApi.AuthentificationFailed, text='authFailed')
	@Online
	@IntentHandler('Bring_addItem')
	@IntentHandler('Bring_whatItem', requiredState='addItem_bringshop', isProtected=True)
	@IntentHandler('SpellWord', requiredState='addItem_bringshop', isProtected=True)
	def addItemIntent(self, session: DialogSession):
		items = self._getShopItems('add', session)
		if items:
			added, exist = self._addItemInt(items)
			self.endDialog(session.sessionId, text=self._combineLists('add', added, exist))


	@AnyExcept(exceptions=BringApi.AuthentificationFailed, text='authFailed')
	@Online
	@IntentHandler('Bring_deleteItem')
	@IntentHandler('Bring_whatItem', requiredState='deleteItem_bringshop', isProtected=True)
	@IntentHandler('SpellWord', requiredState='deleteItem_bringshop', isProtected=True)
	def delItemIntent(self, session: DialogSession):
		items = self._getShopItems('rem', session)
		if items:
			removed, exist = self._deleteItemInt(items)
			self.endDialog(session.sessionId, text=self._combineLists('rem', removed, exist))


	@AnyExcept(exceptions=BringApi.AuthentificationFailed, text='authFailed')
	@Online
	@IntentHandler('Bring_checkList', isProtected=True)
	@IntentHandler('Bring_whatItem', requiredState='checkList_bringshop', isProtected=True)
	@IntentHandler('SpellWord', requiredState='checkList_bringshop', isProtected=True)
	def checkListIntent(self, session: DialogSession):
		items = self._getShopItems('chk', session)
		if items:
			found, missing = self._checkListInt(items)
			self.endDialog(session.sessionId, text=self._combineLists('chk', found, missing))


	@AnyExcept(exceptions=BringApi.AuthentificationFailed, text='authFailed')
	@Online
	@IntentHandler('Bring_readList')
	def readListIntent(self, session: DialogSession):
		"""read the content of the list"""
		items = self.bring().get_items(self.LanguageManager.activeLanguageAndCountryCode)['purchase']
		itemlist = [item['name'] for item in items]
		self.endDialog(session.sessionId, text=self._getTextForList('read', itemlist))


	#### List/Text operations
	def _combineLists(self, answer: str, first: list, second: list) -> str:
		firstAnswer = self._getTextForList(answer, first) if first else ''
		secondAnswer = self._getTextForList(f'{answer}_f', second) if second else ''
		combinedAnswer = self.randomTalk('state_con', [firstAnswer, secondAnswer]) if first and second else ''

		return combinedAnswer or firstAnswer or secondAnswer


	def _getTextForList(self, pref: str, items: list) -> str:
		"""Combine entries of list into wrapper sentence"""
		if not items:
			return self.randomTalk(f'{pref}_none')
		elif len(items) == 1:
			return self.randomTalk(f'{pref}_one', [items[0]])

		value = self.randomTalk(text='gen_list', replace=[', '.join(items[:-1]), items[-1]])
		return self.randomTalk(f'{pref}_multi', [value])
