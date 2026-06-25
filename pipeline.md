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
└── VISITOR — visit tokens i.e. x_repeat substitution
└── TRANSFORMER — class conversion
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

e.g.
code:
```
@cordelia.lpf:del{qn}:radio·talea {3 1 0x6} in 8·dorian d 1 7 3
```
that is the same as:
```
@cordelia.lpf:del{qn}:radio
talea {3 1 0x6} in 8
dorian d 1 7 3
dorian <1 3 9>
```
---
parse without tranformer
```
unit
└── phrase
	├── header
	│   └── cordelia
	├── modifier
	│   └── dot_mod
	│       └── lpf
	├── modifier
	│   └── colon_mod
	│       ├── del
	│       └── array
	│           └── atom
	│               └── qn
	├── modifier
	│   └── colon_mod
	│       └── radio
	└── score
		├── quality
		│   ├── atom
		│   │   └── talea
		│   ├── atom
		│   │   └── array
		│   │       ├── atom
		│   │       │   └── 3
		│   │       ├── atom
		│   │       │   └── 1
		│   │       └── atom
		│   │           └── 0x6
		│   ├── atom
		│   │   └── in
		│   └── atom
		│       └── 8
		└── quality
			├── atom
			│   └── dorian
			├── atom
			│   └── d
			├── atom
			│   └── 1
			├── atom
			│   └── 7
			└── atom
					└── 3
```
	↓
TRANSFORMER
phrase → instrument class
statement → variable class
    
    └── header → name
    └── modifiers → modifiers
    └── score → score

i.e.
```
Instrument(name='cordelia', score=[Quality(items=['talea', Array(items=['1', '2', '3'])])], modifiers=[])
Instrument(name='cordelia', score=[Quality(items=['eu', '3', '8'])], modifiers=[])
Variable(name='var', value=['osc', Array(items=['123', '12'])])
Instrument(
    name='cordelia',
    score=[Quality(items=['osc', Array(items=['123', '12'])]), Quality(items=['var', '3', Array(items=['1', '23', '3']), '1', 'c..'])],
    modifiers=[Modifier(kind='sequence', name='lpf', array=Array(items=['1k'])), Modifier(kind='sequence', name='radio', array=None)]
)
```
   ↓

Now we have only Instrument and Variable.

Instrument
└──name
└──modifiers
└──score

Variable
└──name
└──value: exec func

   ↓
EXPANDER
resolve and translate language subtilities i.e. x2

DEDUCTION
- process score: deduce quality
   ↓
POSTPROCESSOR
- change to Staff class -> .dirty attr
- name: validate name in json, check if already exists in session, create his unique id, send the instrument
- score: process each quality (i.e. dur)
	↓
CSOUND TEMPLATE PRODUCTION
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

