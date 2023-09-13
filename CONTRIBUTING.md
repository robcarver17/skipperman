

## Lint / Black

This project keeps its code pretty with 
[Black](https://black.readthedocs.io/en/stable/). Black gets automatically run 
over any PRs, and the PR won't be merged if it fails. To clean your code
submission manually you'll need Black installed, instructions 
[here](https://black.readthedocs.io/en/stable/getting_started.html). Then
run:
```
black path/to/module.py
```

Or, get your IDE or editor to automatically re-format files as you save. Configuration
instructions [here](https://black.readthedocs.io/en/stable/integrations/editors.html)

Note for pycharm users: The blackd plugin requires a blackd daemon to be running; add it to your crontab.

Or, configure your local git install to automatically check and fix your code
as you commit. Configuration instructions 
[here](https://black.readthedocs.io/en/stable/integrations/source_version_control.html)

### Black version

Black needs to be consistent between the version running in the CI build and your local environment. To check the currently used version, see the `[tool.black]` section of the project TOML file  (https://github.com/robcarver17/pysystemtrade/blob/master/pyproject.toml)

## General code guidelines (INCOMPLETE)


In general, we try and follow the original texts: [PEP 8](https://peps.python.org/pep-0008/) and [clean code](https://gist.github.com/wojteklu/73c6914cc446146b8b533c0988cf8d29).

### General

- Unless there is a single parameter, passed parameters should be explicit as kwargs eg fubar(thing1=thing, thing2=thing2).
- Type hints should be used, with Unions if required `from typing import Union` and Lists / Dicts ...`from typing import List, Dict`
- Verbose doc strings specifying all the parameters are not required (superseded by type hints)

### Naming conventions

- For classes, use CamelCase.
- Common method names are `get`, `calculate`, `read`, `write`.
- Although arguably redundant, I am a fan of describing eg objects that inherit from dicts with a dict_ prefix. This gives hints as to how they behave without having to look at their code.
 

