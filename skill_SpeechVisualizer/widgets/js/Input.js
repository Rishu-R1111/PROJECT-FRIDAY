$(function () {
	function onConnect() {
		MQTT.subscribe('hermes/asr/partialTextCaptured');
		MQTT.subscribe('hermes/asr/textCaptured');
		MQTT.subscribe('hermes/nlu/intentParsed');
		MQTT.subscribe('hermes/asr/stopListening');
		MQTT.subscribe('hermes/asr/startListening');
	}

	function onMessage(msg) {
		//msg to json, get 'text'
		let json = JSON.parse(msg.payloadString);
		if (msg.destinationName == 'hermes/asr/partialTextCaptured') {
			$('#SV_ASRcontentInput')[0].innerHTML = json['text'] + ' ...';
			$('#SV_ASRconf')[0].innerHTML = Number.parseFloat(json['likelihood']).toPrecision(2) * 100 + '%';
		} else if (msg.destinationName == 'hermes/asr/textCaptured') {
			$('#SV_ASRcontentInput')[0].innerHTML = json['text'];
			$('#SV_ASRconf')[0].innerHTML = Number.parseFloat(json['likelihood']).toPrecision(2) * 100 + '%';
		} else if (msg.destinationName == 'hermes/nlu/intentParsed') {
			$('#SV_NLUskill')[0].innerHTML = json['intent']['intentName'];
			$('#SV_NLUconf')[0].innerHTML = Number.parseFloat(json['intent']['confidenceScore']).toPrecision(2) * 100 + '%';
		} else if (msg.destinationName == 'hermes/asr/stopListening') {
			$('#SVI_ICON').attr('class', 'fas fa-microphone-slash');
		} else if (msg.destinationName == 'hermes/asr/startListening') {
			$('#SVI_ICON').attr('class', 'fas fa-microphone');
		}
	}

	mqttRegisterSelf(onConnect, 'onConnect');
	mqttRegisterSelf(onMessage, 'onMessage');
});
