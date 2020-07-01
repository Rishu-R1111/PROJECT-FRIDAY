import sqlite3

from core.base.model.Widget import Widget
from core.base.model.WidgetSizes import WidgetSizes


class CurrentWeather(Widget):

	DEFAULT_SIZE = WidgetSizes.w_small
	DEFAULT_OPTIONS: dict = {'customLocation': ''}

	def __init__(self, data: sqlite3.Row):
		super().__init__(data)


	def baseData(self) -> dict:
		location = self.DEFAULT_OPTIONS.get('customLocation') or self.skillInstance.getConfig('baseLocation').title()
		units = 'C'
		if self.skillInstance.getConfig('units') == 'imperial':
			units = 'F'
		elif self.skillInstance.getConfig('units') == 'kelvin':
			units = 'K'

		return {
			'location': location,
			'units': units,
			'unitsName': self.skillInstance.getConfig('units'),
			'apiKey': self.skillInstance.getConfig('apiKey')
		}
