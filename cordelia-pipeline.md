# CORDELIA PIPELINE

# A BRAND NEW WRITING STYLE
In ISOCORDELIA no commas, no uppercase exist.
We prefer {} to (), but you can use both.

# *CORDELIA*'s PIPELINE
INPUT
	↓
LEXER → list[str]
simply split into chunk the main code
	- split at "@"
	- ignore comments
this chunks are **units**
	↓
PARSER → list[Instrument | Variable]
each unit can either be a **phrase** or a **statement** — they both become staves and they are identified by the same 
	unit
		phrase
			header  cordelia
				modifier
					dot_mod lpf
				modifier
					colon_mod
						del
						array
				modifier
					colon_mod       radio
					score
						quality
							atom    talea
							atom    4
						quality
							atom    d#4
							atom    1
							atom    3#
							atom    4
	↓
TRANSFORMER
Instrument(name='cordelia', qualities=[Talea(pattern=['3', '2'], cycle='8'), Colores(values=[1]), Dur(values=[1]), Dyn(values=[0.28183829312644537]), Env(values=['classic']), Space(values=[1])], modifiers=[], auto_fill=True)
	↓
POSTPROCESSOR
- change to Staff class -> .dirty attr
- name: validate name in json, check if already exists in session, create his unique id, send the instrument
- score: process each quality (i.e. dur)
- modifiers: create template
	↓
VALIDATOR
is the instrument registered?
does the score make sense?
raises clear errors early before anything executes
	↓
SCORE PARSER
lark layer 2 grammar parses the score string
produces structured score data
	↓
DISPATCHER
routes to the right function
taleae/eu.py, taleae/talea.py...
---

todo
- comment syntax and in grammar, if instrument is commented—everything is off
- add possibility of "and" operator to accumulate everything
- set up the recording with pt.record and cs.chn — not inside Csound
