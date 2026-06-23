# CORDELIA REBORN
_a method, a tender organic affection_
_a new horizon_

### FEATURING A BRAND NEW WRITING STYLE
In ISOCORDELIA no commas, no uppercase exist.
We prefer {} to (), but you can use both.
· or newline is everything (but u can also use |)

But w8 — wtf is ISOCORDELIA? Like isorhythm, it could be a live coding style.

## *CORDELIA*'s HOLY PRINCIPLEs
- always start with a **blank empty page**
- **each parameter** has **consequences** and **reaction** on all others 
- **change**, always change even if you are certain. *Progression*, *mouvement* is better than *static thinking*
- play _cordelia_ as the last thing you will ever do in your life
- Have *fun*, be *generous*
- **live coding ≠ cuelist**
- **recompose**, do not repeat
- *repeat* — yep, but only if it is important
- make it **organic** (and ecologic): *code your own choices inside algorithm* (*)
- *viscosity* is everything: everything must be interchangeable. everything must exist at the same time as a parameter. In this direction algorithm becomes *idea* or a *motif* not *pattern*
- if you are thinking language outside composition and sound, u wrong. check [this](https://en.wikipedia.org/wiki/Mind%E2%80%93body_problem).
- **poetry**, please do not forget poetry. Audience read: they must sing and sing loudly in their head.
- linear acceleration/deceleration, random and all other boredom stuff are **banished**, *to speak that word*.
- oh yes, and stop using uppercase (unless u german or after a ".") — useless boring prioritisation (i mean, im really thinking of banning them)

What _Cordelia_ is not: a language to make shitty contemporary music. Use max or ableton for that or all other grm/ircam bullshit.

Live coding to become emancipated cannot repeat itself, it must look in these directions.

(\*) why should we code choises inside algorithm? Live coding gesture is a myth. The organic pattern human expression take to shape an idea is too hard to make it quick enough with some letter. That's why, some choices (and parameters must be interconnected) must exist already inside; attention, not *random* choices, but choice depending on each paramters possibilities (trust me, even with 5 parameters things can become complex).

## *CORDELIA*'s DELIRIUM
why do we need uppercase? why do we need commas?

## *CORDELIA*'s NEWs
- envelopes will have names of chemistry elements — this is called "amazing" (i.e. hyd, oxy, tit, mol, nio)

## *CORDELIA*'s TIPs
- just use one compileOrc at the end not many for each score. just an unique one at the end of the cycle

## *CORDELIA*'s TODO
- comment syntax and in grammar, if instrument is commented—everything is off
- add possibility of "and" operator to accumulate everything
- set up the recording with pt.record and cs.chn — not inside Csound
- taleae and colores under the hood library?

## *CORDELIA*'s PIPELINE

INPUT
	↓
LEXER → list[str]
simply split into chunk the main code
	- split at "@"
	- ignore comments
this chunks are **units**
	↓
PARSER → list[Instrument | Variable]
Parser divide code into 4 levels:
1. each unit can either be a **phrase** or a **statement** — they both become staves and they are identified by the same caracther "@".
---
	2. header | modifier | score (| atom — if it's a statement) this is the main structure of *cordelia*
		- *header* is simply the *variable* or the *instrument name* — this will also be the name of the main Python classes they will be converted in
		- *modifiers* are all the sound modifiers at the end of the chain, they can be parallel (if starts with ":") or in sequence (if "."):
			e.g.
			```
			.fl:del:lpf.del::am

			is

						→ :del			→ out
				.fl 
						→ :lpf.del		→ out

								→ ::am	→ out
			```
		- *score* detain *qualities* (they are simply parameters):
			- rhythm: talea
			- pitches: colores
			- dur
			- dyn
			- env
			- space
			+ info → thinking on adding a dummy quality i can send information to cordelia — i.e. if the chunk is revalidate even if do not change (i.e. `·stubborn` or `mulo`). this can also be funny to add and change qualities..
---
		3. 

e.g.
```
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

	unit
		statement
			header  var
			atom    123
```
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

