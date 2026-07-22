raw source → structured AST
Everything concerned with understanding the input language, independent of what you're eventually compiling to. It doesn't know or care what the output format is.



first step first cordelia receive an entire code.

parser remove comments and separate each lines based on "@"

transformer transform everything or in Instrument or in Variable
let's talk about the step for instrument (in variabale is almost the same but not completely)
so in this passage there's a brief validation about instrument name checked in all the keyword json data of cordelia (i dont know if its necessary to have it here, but its not hard to wrrite because it's just few lines). so after the validation and the transformation of some in class. i dont know if i could add a step of a further mini step of macro substitution i dont know how to call it but things not so relevant for the further step and that its the same for every code (like ^2 is the multiplication code, this means that "e^3" in cordelia means "e e e"). after these step i probabily want to add a step to check a "zero state" what i mean by that is that its a first comparison with the code of before and see if any of these elements are the same aas before (maybe with hash) just to know it elements are changed or no more there or first time there (init or spawn).

then what i called the deduce step this means that each main part of an instrument (name, modifier, qualities) are processed.. like in name (add a unique identifier for the instrument) then does csound know the instrument ? yes continue, no emit to csound. then the modifier does csound know? no create a class that parse and detect from csound udo orc the parameters of the udo and then add this to the modifier class. if its known just retrive the udo class and add to the modifier class. in this phase there's also a parse for everything that its not parsed inside the modifiers (because what is happening is that some class has different meaning based on context). for e.g.


@tiny·eu 4 8 in 4·edo31hex d {1 2 5 7}^4 {1 2 4 7}^4·dur*2

here "dur*2" is an expression, but it is for python it should not be sent like this to csound. while @tiny.del(50+osc(2 3)) this "50+osc(2 3)" should be sent enteriely

now ther's also the qualities where thoughs a carefully designed plugin system in python they can process each qualities based on some matching system. this is tricky because what i'd like to add is that in a code like this:

@tiny·eu 4 8 in 4·edo31hex d {1 2 5 7}^4 {1 2 4 7}^4·dur*2

we could write also

@tiny·eu 4 8 in 4·edo31hex d {1 2 5 7}^4 {1 2 4 7}^3·same [2] e

where "same [2] e" means : the same quality as before but the second element of the quality ("d") becomes "e". and again 

@tiny·eu 4 8 in 4·edo31hex d {1 2 5 7}^4 {1 2 4 7}^3·same [2] e

@aaron·same talea as tiny

where "same talea as tiny" means that he must know everytime for each quality all the information updated of each instrument (how could i build that)
---
then there's a process pahses where eventually qualitis missing are filled with default qualities.
then in eevry items we check if there are any items that csound must know and he doesnt
then we sum each qaulities creating a final unique quality for each important quality

the we compare again maybe with everything before because maybe its important to check.

after that there's a fina phase of conversion to csound.




//

lex        raw source string arrives

parse      strip comments
           split into raw statement units on "@"

transform  raw unit -> typed node (instrument | variable)
   ├─ name validation      check against keyword json (light, syntactic)
   └─ macro expansion      context-free rewrites, same for every code
                           (e^3 -> e e e, i.e. ^n = repeat)

triage     hash each unit against prior session state
           tag: unchanged | removed | new (init/spawn)
           <- this is your "zero state" step; see Q1 below

deduce     per instrument, three sub-passes:
   ├─ name      
   │            csound knows it? yes -> continue / no -> queue definition
   ├─ modifier  csound knows the udo? 
   │            no  -> parse .orc, build udo class
   │            yes -> retrieve cached udo class
   │            + context-aware sub-parse of inner expressions
   │              (python-eval "dur*2" vs pass-through "50+osc(2 3)")
   └─ quality   corpus/plugin match per quality type
                resolve "same [n] v" and "same X as Y" against wisdom

learn      fill missing qualities with defaults
           flag remaining unknowns csound still needs
           merge qualities -> one final quality set per instrument
           write result back into wisdom

compare    final resolved state vs previous resolved state

offer      (tbd — staging before emission)

emit       csound conversion  <- later, per your note

//

cordelia/
├── pyproject.toml
├── README.md
├── cordelia/
│   ├── __init__.py
│   ├── pipeline/                 # the 9 stages — orchestration only, no domain logic
│   │   ├── __init__.py
│   │   ├── lex.py
│   │   ├── parse.py              # comment strip, split on @, macro substitution
│   │   ├── transform.py          # raw unit -> instrument | variable
│   │   ├── triage.py             # zero-state hash check
│   │   ├── deduce/
│   │   │   ├── __init__.py
│   │   │   ├── name.py
│   │   │   ├── modifier.py
│   │   │   └── quality.py
│   │   ├── learn.py              # defaults, merge, write back to wisdom
│   │   ├── compare.py            # final resolved-state diff
│   │   ├── offer.py
│   │   └── emit.py               # csound conversion
│   │
│   ├── model/                    # the nouns — plain data/behavior, no pipeline awareness
│   │   ├── __init__.py
│   │   ├── instrument.py
│   │   ├── variable.py
│   │   ├── modifier.py
│   │   ├── quality.py
│   │   └── udo.py                # class built from a parsed csound UDO
│   │
│   ├── wisdom/                   # the session-state store, read/written across the whole pipeline
│   │   ├── __init__.py
│   │   ├── store.py              # per-instrument, per-quality history — what "same X as Y" queries
│   │   └── hashing.py            # shared by triage and compare
│   │
│   ├── corpus/                   # the quality plugin shell
│   │   ├── __init__.py
│   │   ├── base.py               # plugin protocol
│   │   ├── registry.py           # matching/dispatch by quality type
│   │   └── plugins/
│   │       ├── talea.py
│   │       ├── edo.py
│   │       └── same_ref.py       # handles "same [n] v" and "same X as Y"
│   │
│   ├── keywords/                 # static json + loader, used by transform's name validation
│   │   ├── __init__.py
│   │   ├── data/keywords.json
│   │   └── loader.py
│   │
│   ├── csound/                   # everything that talks to csound — deduce's lookups AND final emit
│   │   ├── __init__.py
│   │   ├── orc_parser.py         # parses .orc UDOs into model/udo.py instances
│   │   ├── registry.py           # what csound already knows (instruments, udos)
│   │   └── templates/
│   │       └── instrument.csd.j2
│   │
│   └── errors.py
│
├── tests/
│   ├── pipeline/
│   ├── model/
│   ├── wisdom/
│   └── corpus/
└── docs/