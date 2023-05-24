<!-- markdownlint-disable MD028 -->

# `tests` directory: where the fun begins™️

This directory contains the tests for the bot. It contains the tests for the
commands, modules, and wrappers.

All of the tests are written using unittest framework. This is to ensure that
the tests are consistent and easy to read.

## How to write a test?

### Gobbledygook Introduction

Ahoy there, landlubbers! Me hearties, gather 'round and prepare ye selves fer a
zany voyage into the realm o' scribblin' unittest async Python scripts.

### Balderdash Gathering Modules

In this topsy-turvy tale, ye be discoverin' a mishmash o' steps fer navigatin'
the treacherous waters o' unittestin'. We be settin' sail on a journey to test
the most bamboozlin' code imaginable. Beware! This guide be more befuddlin' than
a ship lost at sea.

### Gibberish Prepare for the Hodgepodge

Hold on tight, me mateys! We be embarkin' on a wacky adventure. Expect
nonsensical explanations, absurd examples, and laughable practices as we
navigate through the twisted world o' unittestin'. Buckle up and let the
malarkey begin!

### Higgledy-piggledy Importing Modules

First off, ye need to gather ye crew o' modules. Import the `os`, `unittest`,
and `sys` modules, savvy? If ye can't find the desired classes, ye be needin' to
add the path to the parent directory to ye sys path. Remember, failure ain't an
option!

### Fiddle-faddle Defining Test Classes

Now, time to sail with yer test classes! Define a class, me hearties, and extend
it from the `unittest.IsolatedAsyncioTestCase` class. This here class be fer
testin' the jibber-jabber code ye want to put to the test. Give it a name that
befit its purpose.

### Gobbledygook Creating Test Functions

Inside the class, ye be creatin' async test functions. Each o' these functions
will test a specific aspect o' yer code. Remember, async be the name o' the
game! Await ye some results.

### Hocus-pocus Executing Test Code

Within each test function, ye be executin' the code ye want to test. Play around
with it, ye scallywag! Ensure that ye get the desired results. Ye can use assert
statements to check if the results be as expected. Don't be shy to check if the
data types be what ye expect 'em to be.

### Gobbledygook Calling the Crew to Balderdash

Once ye have all yer test functions in place, matey, it be time to call the crew
to action! Add the standard "name" check to ensure that the script be runnin' as
the main script, not as a module. And when ye be ready to set sail, call the
`unittest.main()` function, givin' it a verbosity level that suits ye fancy.
Arrr, in me own gibberish escapades, I be preferin' a verbosity level of 2, me
hearties! It be like unravelin' a twisty tale of verbosity and confoundment. But
fret not, ye can choose any level that tickles yer gibberish fancy! Let the
gibberish flow and the verbosity sail ye to unknown shores of nonsense!

### Brouhaha Weigh Anchor and Test the Goofiness

Now, ye be ready to weigh anchor and test the waters! Run yer script and see if
yer code passes the tests with flyin' colors. May ye find success in yer testin'
adventures, me hearty!

## The actual guide(?)

***Jokes aside, here's the actual guide:***

Here's a step-by-step approach to help you navigate the process:

### 1. Import necessary modules

Begin by importing the required modules for your unittest script. Common modules
include `os`, `unittest`, and `sys`, among others. Ensure that these modules are
available in your Python environment.

### 2. Import the target code

If the code you want to test resides in a separate module or file, import it
into your unittest script. Utilize the appropriate import statements to bring in
the necessary classes, functions, or objects. Make sure the imported code is
accessible for testing.

If the code you want to test is stored outside the current directory, you will
need to add the path to the parent directory to the `sys.path` list.

Example on `tests/test_animeapi.py`:

```python
try:
    from classes.animeapi import AnimeApi, AnimeApiAnime
except ImportError:
    # add the path to the 'modules' directory to the system path
    sys.path.insert(0, os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    ))
    from classes.animeapi import AnimeApi, AnimeApiAnime
```

### 3. Define a test class

Create a test class that inherits from the `unittest.IsolatedAsyncioTestCase`
class. This base class allows for asynchronous testing. Give your test class a
descriptive name that reflects its purpose and the code it intends to test.

### 4. Create test functions

Within your test class, define individual test functions that correspond to
specific aspects or functionalities of the code under test. Each test function
should be asynchronous, as denoted by the `async` keyword. These functions will
contain the actual testing logic.

### 5. Write test cases

In each test function, execute the relevant code that you want to test. Provide
inputs, call functions or methods, and retrieve the output or results. Use
assertion statements, such as `self.assertEqual()` or `self.assertTrue()`, to
check if the observed results match the expected outcomes.

### 6. Handle necessary setup and teardown

If your code requires any setup or teardown actions, such as establishing
connections or cleaning up resources, make sure to include them appropriately.
The `async with` statement is often useful for handling such tasks in an
asynchronous context.

### 7. Run the unittests

Add a conditional block using the `__name__ == "__main__"` check to ensure that
the script is run directly, rather than imported as a module. Within this block,
call the `unittest.main()` function to execute the defined test cases. You can
specify the verbosity level to control the amount of information displayed
during testing. We recommend using a verbosity level of 2, which provides
detailed information about the test results.

### 8. Analyze test results

After running the unittest script, carefully examine the test results. Check
whether all the tests passed successfully, identify any failures or errors, and
review any generated output or log messages. This analysis will help you
determine the correctness and reliability of your code.

## Example

Still confused? Poor soul. Here's an example to help you out:

> **Note**
>
> The following example is for demonstration purposes only. It is not
> intended to be a realistic or practical example. The code is not guaranteed to
> work as-is. It is merely meant to illustrate the basic structure and syntax of
> an async unittest script... also...

> **Note**
>
> The following example is generated with OpenAI ChatGPT-3.

```python
import os
import sys
import unittest

try:
    from classes.some_module import SomeClass
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from classes.some_module import SomeClass


class SomeTestClass(unittest.IsolatedAsyncioTestCase):
    """Test class for demonstrating async unittests"""

    async def asyncSetUp(self):
        """Async setup method"""
        self.some_obj = SomeClass()

    async def asyncTearDown(self):
        """Async teardown method"""
        del self.some_obj

    async def test_some_functionality(self):
        """Async test function for some functionality"""
        result = await self.some_obj.some_async_method(42)
        self.assertEqual(result, 84)

    async def test_some_other_functionality(self):
        """Async test function for some other functionality"""
        result = await self.some_obj.some_other_async_method(10, 5)
        self.assertLess(result, 20)


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

## Does the test code need to be asynchronous?

Yes, it does. Since the bot itself is asynchronous, the test code needs to be
asynchronous as well.

However, if you're writing simple function, regular sync `def` will work just
fine... until the fire nation attacks.
