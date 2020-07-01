from typing import Optional

from youtube_api import YouTubeDataAPI

from core.ProjectAliceExceptions import SkillStartingFailed
from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class YoutubeAPI(AliceSkill):
	"""
	Author: Psychokiller1888
	Description: Access and manage your youtube account
	"""


	def __init__(self):
		super().__init__()
		try:
			self._youtube: Optional[YouTubeDataAPI] = None
		except ValueError:
			raise SkillStartingFailed('Youtube api key not valid')


	def onStart(self):
		super().onStart()
		self._youtube = YouTubeDataAPI(self.getConfig('youtubeApiKey'))
		if not self._youtube.verify_key():
			raise SkillStartingFailed('Youtube api key not valid')


	@IntentHandler('GetYoutubeChannelStats')
	def getChannelStats(self, session: DialogSession, **_kwargs):
		metadata = self._youtube.get_channel_metadata('')

		if not metadata:
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk(text='error'))
			return

		print(metadata)

		self.endDialog(sessionId=session.sessionId, text=self.randomTalk(text='myText', replace=[sub]))
