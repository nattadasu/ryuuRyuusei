<!-- markdownlint-disable MD033 -->
<!-- omit in toc -->
# Contributing to Project

Hello there! If you're reading this, then you're probably interested in
contributing to this project. This document will guide you through the process
of contributing to this project.

<!-- omit in toc -->
## Table of Contents

- [Code Development](#code-development)
  - [Forking the Repository](#forking-the-repository)
  - [Additional Dependencies](#additional-dependencies)
  - [Adding New Commands](#adding-new-commands)
  - [Adding New API Integrations from 1st or 3rd Party](#adding-new-api-integrations-from-1st-or-3rd-party)
  - [Formatting, Linting, Batch Testing, and Coverage Reporting](#formatting-linting-batch-testing-and-coverage-reporting)
- [Other Ways to Contribute](#other-ways-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting New Features](#suggesting-new-features)
  - [Improving the Documentation](#improving-the-documentation)
  - [Donating to the Project](#donating-to-the-project)
  - [Starring the Repository](#starring-the-repository)

## Code Development

This guide is intended for those who want to contribute to the code development
of this project. If you're looking for other ways to contribute, please read
[Other Ways to Contribute](#other-ways-to-contribute) section.

### Forking the Repository

You obviously need to fork this repository and clone it to your local machine.

Then you may read the any documents related on contributing, you can find most
of the documents in `tests`, `modules`, `extensions`, and `classes` directory
on `README.md` file. Each classes and modules has been heavily documented
regarding their usage and implementation.

"*why not make a docs web?*" you may ask... I personally don't think it's
necessary to make a docs web for this bot, as it's not a library or framework
that needs to be documented. It's just a bot, and I think it's better to read
the documentation directly from the class, module, or function itself.

You may also accepts [Code of Conduct](CODE_OF_CONDUCT.md) and [LICENSE](LICENSE)
regarding your contribution and modification.

You need to know some stuff about what we've been doing in this bot:

- All 3rd APIs were separated to each file in `classes` directory as... class.
- All data spit by API are dataclasses, unless it's not possible as some key may
  not documented properly, missing, or... both (im looking at you, SIMKL).
- `Enum` is basically fancier `Literal`, and you can assign synonym with same
  value. However, this is not mandatory, but highly recommended.
- Classes must have their own test file in `tests` directory.
- Classes must be run with `with` statement to ensure the connection on `aiohttp`
  is closed properly.
- Classes should have auto caching mechanism saved as JSON file in `cache`
  directory, unless if the method is always changing, such as `get_user` method.
- All commands were grouped and placed in `extensions` directory.
- Classes, functions, methods, immutable variables, or even the script itself
  are documented with docstrings.
- All functions and variables must be statically typed to prevent any
  unexpected errors.
- Naming convetions:
  - `UpperCamelCase` for classes, dataclass, and enum
  - `UPPER_SNAKE_CASE` for immutable variables
  - `snake_case` for functions, methods, mutable variables, and file name
  - `lowercase` for extension file name
  - `spaced lowercase` for command name, consist of:
    - `command` * the command name
    - `group` * the command group
    - `subcommand` * the subcommand name
- Project must pass all tests and CI/CD before merging to branch.

### Additional Dependencies

Before you can start developing the bot, you need to install additional
dependencies. Execute the following command:

```bash
pip install -U -r requirements-dev.txt
```

### Adding New Commands

1. Create a new file in the `extensions` directory with the following format:

   ```python
   import interactions as ipy

   class Example(ipy.Extension):
       def __init__(self, bot):
           self.bot = bot

       @ipy.slash_command(
        name="example",
        description="Example command",
       )
       async def example(self, ctx: ipy.SlashContext) -> None:
           await ctx.send("Example")

   def setup(bot):
       Example(bot)
   ```

2. ???
3. Run the bot via `python main.py` and test the command.
4. Profit!

### Adding New API Integrations from 1st or 3rd Party

1. Create a new file in the `classes` directory
2. Read carefully the instruction written in [`classes/README.md`](classes/README.md)
3. Write test script in `tests` directory then run it
4. Integrate the class to the commands if test passed

### Formatting, Linting, Batch Testing, and Coverage Reporting

You can easily do all that stuff by just running `dev.py` script.

```bash
python dev.py
```

However, autoformat the scripts requires your confirmation, as default
configuration of this repo is based on DeepSource's configuration, which
is **a lot** different than the default configuration of `autopep8`.

If you acknowledge the risk, type `y` if asked.

## Other Ways to Contribute

If you're not interested in contributing to the code development, you can
contribute in other ways, such as:

### Reporting Bugs

If you found any bugs, please report it to the [Issues](https://github.com/nattadasu/ryuuRyuusei/issues)
section. Please make sure that the bug you're reporting is not a duplicate of
existing issue.

### Suggesting New Features

Suggesting new features is also a way to contribute to this project. You can
suggest new features by following similar steps as [Reporting Bugs](#reporting-bugs).

### Improving the Documentation

Found any typos or grammatical errors in the documentation? You can fix it by
submitting a pull request to this repository... Though, you can also just
[report it](#reporting-bugs) if you're confused on how to fix it.

### Donating to the Project

If you're interested in donating to the project, you can do so by pressing
<kdb>❤️ Sponsor</kdb> button on the top of this page. You can also donate to
the project by sending some money to my [PayPal](https://paypal.me/nattadasu) or
[Ko-fi](https://ko-fi.com/nattadasu).

Kewarganegaraan Indonesia dan tinggal di Indonesia? Kamu bisa juga donasi ke
[Trakteer](https://trakteer.id/nattadasu) atau [Saweria](https://saweria.co/nattadasu).

### Starring the Repository

By starring this repository, you're helping this project to be more visible to
other people. This will also help the project to be more popular, and more
people will use this bot.

Whatever you do, we appreciate your contribution to this project! 😉
