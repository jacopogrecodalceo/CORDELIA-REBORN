# CORDELIA PIPELINE

   INPUT
      ↓
   PARSER
   flat list of staff/score tokens
         ↓
   GROUPER
   pair each staff with its following score
   produces: [Group(staff='p', score='120'), Group(staff='cordelia', score='talea 3 1')]
         ↓
   CLASSIFIER
   for each group: is staff an instrument or variable?
   looks at JSONs
   produces: [{type: "instrument", name: "cordelia", score: "talea 3 1"}, ...]
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

staff:
- instrument
- modifier
- variable

This is a classic phase-based scheduler — the same approach used by TidalCycles internally.
