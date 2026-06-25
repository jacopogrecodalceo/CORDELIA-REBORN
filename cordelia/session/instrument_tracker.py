# instruments.py
import threading

_instruments = set()
_lock = threading.Lock()

def add(name):
	with _lock:
		_instruments.add(name)

def remove(name):
	with _lock:
		_instruments.discard(name)

def has(name):
	with _lock:
		return name in _instruments

def get_all():
	with _lock:
		return set(_instruments)

def clear():
	with _lock:
		_instruments.clear()

def count():
	with _lock:
		return len(_instruments)