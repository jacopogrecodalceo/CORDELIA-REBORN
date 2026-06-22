def organise_devs(devs: dict):
	"""
	{'device_name': 'jacques Focal Bathys [Core Audio, 1 in, 0 out]', 'device_id': 'adc0', 'rt_module': 'PortAudio', 'max_nchnls': 1, 'isOutput': False}, {'device_name': 'BlackHole 16ch [Core Audio, 16 in, 16 out]', 'device_id': 'adc1', 'rt_module': 'PortAudio', 'max_nchnls': 16, 'isOutput': False}, {'device_name': 'BlackHole 2ch [Core Audio, 2 in, 2 out]', 'device_id': 'adc2', 'rt_module': 'PortAudio', 'max_nchnls': 2, 'isOutput': False}, {'device_name': 'MacBook Pro Microphone [Core Audio, 1 in, 0 out]', 'device_id': 'adc3', 'rt_module': 'PortAudio', 'max_nchnls': 1, 'isOutput': False}, {'device_name': 'jacques iphone Microphone [Core Audio, 1 in, 0 out]', 'device_id': 'adc4', 'rt_module': 'PortAudio', 'max_nchnls': 1, 'isOutput': False}, {'device_name': 'Messenger Loopback Audio [Core Audio, 2 in, 2 out]', 'device_id': 'adc5', 'rt_module': 'PortAudio', 'max_nchnls': 2, 'isOutput': False}, {'device_name': 'ZoomAudioDevice [Core Audio, 2 in, 2 out]', 'device_id': 'adc6', 'rt_module': 'PortAudio', 'max_nchnls': 2, 'isOutput': False} 
	"""
	organised_dict = {}
	for d in devs:
		organised_dict[d['device_name']] = {
			'id': d['device_id'],
			'max_nchnls': d['max_nchnls'],
		}
	return organised_dict