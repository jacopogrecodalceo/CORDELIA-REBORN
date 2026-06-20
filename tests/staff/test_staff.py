# tests/test_staff.py
import pytest
from syrupy.assertion import SnapshotAssertion
from cordelia.staff.model import Staff
from cordelia.staff.renderer import StaffRenderer


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def basic_staff() -> Staff:
	return Staff(
		instrument='violin',
		talea_raw=[1, 0, 1, 1, 0],
		colores=['c4', 'e4'],
		staff_dur=4.0,
	)

@pytest.fixture
def renderer() -> StaffRenderer:
	return StaffRenderer()


# ── unit: Staff model ─────────────────────────────────────────────────────────

def test_talea_computed(basic_staff):
	assert basic_staff.talea == [1, 0, 2, 3, 0]

def test_dur_derived(basic_staff):
	# should auto-derive from talea when not provided
	assert len(basic_staff.dur) > 0

def test_dyn_derived_length(basic_staff):
	assert len(basic_staff.dyn) == len(basic_staff.dur)

def test_update_sets_dirty(basic_staff):
	assert not basic_staff.dirty
	basic_staff.update(staff_dur=8.0)
	assert basic_staff.dirty
	assert basic_staff.staff_dur == 8.0

def test_update_unknown_param_ignored(basic_staff):
	basic_staff.update(nonexistent='x')
	assert not basic_staff.dirty


# ── snapshot: rendered Csound output ─────────────────────────────────────────

def test_born_render(snapshot: SnapshotAssertion, basic_staff, renderer):
	output = renderer.render(basic_staff)
	assert output == snapshot

def test_update_render(snapshot: SnapshotAssertion, basic_staff, renderer):
	renderer.render(basic_staff)          # born pass
	basic_staff.update(staff_dur=8.0)
	output = renderer.render(basic_staff) # update pass
	assert output == snapshot

def test_born_sets_born_false(basic_staff, renderer):
	assert basic_staff.born
	renderer.render(basic_staff)
	assert not basic_staff.born

def test_flush_clears_score(basic_staff, renderer):
	renderer.render(basic_staff)
	assert len(renderer.score) == 1
	renderer.flush()
	assert len(renderer.score) == 0