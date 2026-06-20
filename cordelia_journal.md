## 360617
i am focusing on how to manage the new schedule bridge between Csound and Python.
One main problem is that if i use the cs.scoreEvent when csound is running offline the two clokc (python's and csound) are not sync. The result is something completely different..
So, another option I already tried was to control a table in csound gathering all rhythmic information 