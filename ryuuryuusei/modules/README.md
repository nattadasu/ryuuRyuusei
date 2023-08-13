# `modules` directory

This directory contains the modules for the bot. It contains broader features
or functionalities of functions or immutable global constant that can be used by
the bot or `classes`, either required or optional.

## What is the difference between `modules` and `classes`?

As the name implies, `classes` is a script that contains classes (and sometimes
additional enums and dataclasses) that can be used by the bot and may tied to
functions or methods in `modules`, that if deleted, will cause the bot to not
work properly.

Meanwhile, `modules` is a script that contains functions or immutable global
constant that can be used by the bot or `classes`, mostly optional. If deleted,
the bot will still work properly, but some features may not work as intended.

However, if you deleted `/modules/const.py`, the bot will not work at all...
since you've deleted the constants, duh.

## What things I need to know before writing a module?

**Nothing**, really. But as a general rule of thumb, you should write a module
if you think that the function or constants are used by more than one script,
and quite repetitive to write.

Though, if you want to write a module, you should follow these guidelines:

* The module must be properly documented. This means that you need to document
  every function, class, and method in your code. You can easily do this by
  using docstrings.
* The module must be type hinted. This means that you need to use type
  annotations in your code really well.
* Oh also, you must write expected return type for each function or method in
  your code, like this:

  ```py
  def foo(bar: str) -> str:
      return bar
  ```

  See, there's a `-> str` after the parameter list? That's the expected return
  type.
* ~~The module must have their own test script on `/tests` directory.~~ Nah,
  you don't need to do this. But if you want to, you can do it.

## How to write a module?

> **Note**
>
> Example on this section is generated automatically by GitHub Copilot.

You can use the existing modules as a reference. This is the general structure
of a module:

```py
# `modules/foo.py`

"""This module contains the `foo` function."""

from typing import Any

def foo(bar: str) -> Any:
    """This function does something.

    Parameters
    ----------
    bar : str
        Some parameter.

    Returns
    -------
    Any
        Some return value.
    """
    return bar
```

## How to use a module?

import. that's it.

```py
# `bar.py`

"""This script contains the `bar` function."""

from modules.foo import foo

def bar(baz: str) -> str:
    """This function does something.

    Parameters
    ----------
    baz : str
        Some parameter.

    Returns
    -------
    str
        Some return value.
    """
    return foo(baz)
```
