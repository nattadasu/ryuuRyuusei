# `classes` directory

This directory contains the classes that mostly responsible for talking to the
3rd party APIs. The classes are named after the 3rd party API they are used
by the bot. For example, `classes/jikan.py` is used to talk to the Jikan API.

Or it will talk to its own 1st party API (`database`, `nekomimidb`, `animeapi`),
which is used to fetch local data.

Or it will also handle exceptions classes (`exceptions`), which is used to
define custom exceptions.

## But why don't you use any of the existing API wrapper packages?

Mostly all the wrappers I found were not asynchronous-ready (relies on
`requests` library) and the bot itself requires the use of asynchronous code
to work properly.

Even though there are also packages that are asynchronous-ready, they are
not properly documented, type hinted, not actively maintained, or even worse,
broken in some way.

So I decided to write my own wrappers instead, this way I can ensure that the
wrappers does what I want them to do, and even better, those wrappers are
properly documented and type hinted.

## What things I need to know before writing a wrapper?

Most of the scripts in this directory are written in a way that they are
independent from the bot itself. This means that you can use them in your
own project without having to install the bot itself.

However, there are some things you need to know before writing a wrapper:

* The wrapper must be asynchronous-ready. This means that you need to use
  `aiohttp` library instead of `requests` library.

* The wrapper must be type hinted. This means that you need to use type
  annotations in your code, enumerations, and dataclasses. You could, however,
  uses `TypedDict` instead of dataclasses if you want to, but personally I
  would like to avoid it (as it can look ugly sometimes, no offense).

  The only exception with not using dataclass or `TypedDict` is when the
  3rd party API returns a JSON object that may contains undocumented keys,
  missing keys than using `null`/`None` value, or even worse, both. In this
  case, you can just return as `dict` instead. *I'm looking at you, SIMKL.*

* The wrapper must be properly documented. This means that you need to
  document every function, class, and method in your code. You can easily
  do this by using docstrings.

* The wrapper must be run in `with` statement. This means that you need to
  use `async with` statement in your code. This is to ensure that the
  `aiohttp.ClientSession` is properly closed after the wrapper is done
  doing its job.

* The wrapper must have their own test script on `/tests` directory. This
  means that you need to write a test script for your wrapper. It ensures
  that your wrapper is working properly.

## How to write a wrapper?

> **Note**
>
> Example on this section is generated automatically by GitHub Copilot.

You can use the existing wrappers as a reference. This is the general
structure of a wrapper:

```py
import aiohttp
from typing import Optional
from dataclasses import dataclass
from enum import Enum

class SomeEnum(Enum):
  """Some enum."""
    SOME_ENUM_VALUE = "some_enum_value"
    """Some enum value."""
    ENUMS_WITH_SYNONYMS = SYNONYM = "enums_with_synonyms"
    """Some enum value with synonyms."""

@dataclass
class SomeDataclass:
  """Some dataclass."""

  some_dataclass_field: str
  """Some dataclass field."""
  enums: Optional[SomeEnum] = None
  """Some enum field."""

class SomeWrapper:
  """Some wrapper."""

  def __init__(self):
    """Initialize the wrapper."""
    self.session = None

  async def __aenter__(self):
    """Enter the wrapper."""
    self.session = aiohttp.ClientSession()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Exit the wrapper."""
    await self.close()

  async def close(self):
    """Close the wrapper."""
    await self.session.close()

  async def some_method(
    self,
    some_argument: Union[str, int],
    some_optional_argument: Optional[str] = None,
    some_literal_argument: Literal["some_literal_value"] = "some_literal_value"
  ) -> SomeDataclass:
    """Some method.

    Parameters
    ----------
    some_argument : Union[str, int]
        Some argument.
    some_optional_argument : Optional[str], optional
        Some optional argument, by default None
    some_literal_argument : Literal["some_literal_value"], optional
        Some literal argument, by default "some_literal_value"

    Returns
    -------
    SomeDataclass
        Some dataclass.
    """
    # Do something here
    return SomeDataclass("some_dataclass_field", SomeEnum.SOME_ENUM_VALUE)
```

## How to use a wrapper?

You can use the wrapper like this:

```py
from classes.some_wrapper import SomeWrapper

async def main():
  async with SomeWrapper() as some_wrapper:
    some_dataclass = await some_wrapper.some_method("some_argument")
    print(some_dataclass.some_dataclass_field)
    print(some_dataclass.enums)
```
