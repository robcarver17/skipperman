


## General code guidelines (INCOMPLETE)


In general, we try and follow the original texts: [PEP 8](https://peps.python.org/pep-0008/) and [clean code](https://gist.github.com/wojteklu/73c6914cc446146b8b533c0988cf8d29).

### General

- Unless there is a single parameter, passed parameters should be explicit as kwargs eg fubar(thing1=thing, thing2=thing2).
- Type hints should be used, with Unions if required `from typing import Union` and Lists / Dicts ...`from typing import List, Dict`
- Verbose doc strings specifying all the parameters are not required (superseded by type hints)

### Naming conventions

- For classes, use CamelCase.
- Although arguably redundant, I am a fan of describing eg objects that inherit from dicts with a dict_ prefix. This gives hints as to how they behave without having to look at their code.
 

