from loguru import logger

def _check_if_duplicates(pending_poems):
	poems = {}
	duplicates = []
	for poem in pending_poems:
		if poem.uid in poems:
			duplicates.append(poem)
			continue
		poems[poem.uid] = poem

	if duplicates:
		uid = duplicates[0].uid
		logger.warning(f"ignored duplicate uids: {uid =}")
		del poems[uid]

	return poems

session_poems = {}

def compare(pending_poems):
	pending_poems = _check_if_duplicates(pending_poems)

	compared_poems = []
	init_keys = pending_poems.keys() - session_poems.keys()
	release_keys = session_poems.keys() - pending_poems.keys()
	common_keys = pending_poems.keys() & session_poems.keys()


	for k in init_keys:
		poem = pending_poems[k]
		poem.state = 'init'
		session_poems[k] = poem
		compared_poems.append(poem)

	for k in release_keys:
		poem = session_poems.pop(k)
		poem.state = 'release'
		compared_poems.append(poem)

	for k in common_keys:
		poem = pending_poems[k]
		previous = session_poems[k]
		poem.state = 'patched' if poem != previous else 'unpatched'
		poem.is_playing_instr = previous
		session_poems[k] = poem
		compared_poems.append(poem)

	return compared_poems