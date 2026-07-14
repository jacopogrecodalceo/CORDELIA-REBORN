class Session:
	def __init__(self):
		self.poems = dict()

	def add(self, poem):
		self.poems[poem.uid] = poem

	def get(self, uid):
		return self.poems[uid]

	def remove(self, uid):
		del self.poems[uid]

	def reconcile(self, pending_poems):
		init_keys = pending_poems.keys() - self.poems.keys()
		release_keys = self.poems.keys() - pending_poems.keys()
		common_keys = pending_poems.keys() & self.poems.keys()

		changed = []

		for k in init_keys:
			poem = pending_poems[k]
			poem.state = 'init'
			self.poems[k] = poem
			changed.append(poem)

		for k in release_keys:
			poem = self.poems.pop(k)
			poem.state = 'release'
			changed.append(poem)

		for k in common_keys:
			poem = pending_poems[k]
			previous = self.poems[k]
			poem.state = 'patched' if poem != previous else 'unpatched'
			poem.is_playing_instr = previous
			self.poems[k] = poem
			changed.append(poem)

		return changed

session = Session()