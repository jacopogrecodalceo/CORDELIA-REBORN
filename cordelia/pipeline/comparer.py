from loguru import logger
from cordelia.registry import session

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

def compare(pending_poems):
	cleaned_poems = _check_if_duplicates(pending_poems)
	cleaned_poems = session.reconcile(cleaned_poems)
	for poem in cleaned_poems:
		session.add(poem)
	return cleaned_poems