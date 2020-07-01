(function () {

	function getIconName(val) {
		let fileName = val.toLowerCase();
		let repl = {
			"\\s": "_",
			" ": "_",
			"-": "_",
			"!": "",
			"\xe4": "ae",
			"\xf6": "oe",
			"\xfc": "ue",
			"\xe9": "e"
		};
		let n = new RegExp(Object.keys(repl).join("|"), "gi");
		fileName = fileName.replace(n, function (t) {
			return repl[t.toLowerCase()]
		});
		return fileName + '.png'
	}


	function refresh() {
		$.ajax({
			url: '/home/widget/',
			data: JSON.stringify({
				skill: 'BringShoppingList',
				widget: 'BringShoppingList',
				func: 'getList',
				param: ''
			}),
			contentType: 'application/json',
			dataType: 'json',
			type: 'POST'
		}).done(function (answer) {
			let listItems = "";
			$.each(answer, function (i, val) {
				listItems += '<div class="tile">' +
					'<div class="BringShoppingTile_imgCont"></div>' +
					'<img class="BringShoppingItemIcon" src="https://web.getbring.com/assets/images/items/' + getIconName(val['image']) +
					'" onerror="this.onerror=null; this.src=\'https://web.getbring.com/assets/images/items/' + val['image'][0].toLowerCase() + '.png\';" /><br/>' +
					val['text'] + '</div>';
			});
			$('#BringShoppingList_list').html(listItems);
		});
	}

	refresh();
	setInterval(function () {
		refresh()
	}, 1000 * 20);

})();
