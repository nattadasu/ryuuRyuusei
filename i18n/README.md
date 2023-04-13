# Internationalization Guide

Hello and thank you for your interest to translating this bot! This guide will
help you to get started with translating the bot.

For your information, the bot is only officially supported in 2 languages:
English and Indonesian. However, you can still translate the bot to your
language if you want to.

All translations must be saved as YAML (`*.yaml`) file, and must be placed in
the `i18n` directory. The file name must be in the format of
`<lang><_<script>><region>`, where:

* `<lang>` is the language code, in lowercase. For example: `en` for English,
  `id` for Indonesian, `zh` for Chinese, etc.
* `<_<script>>`, if present, is the script code, in lowercase. For example:
  `zh_hans` for Simplified Chinese, `zh_hant` for Traditional Chinese, etc.
* `<region>`, is 2-3 alphanumerical region code, in uppercase. For example:
  `US` for United States, `GB` for Great Britain, etc.

Exclusion only applies to following:

* `ar_001`: Arabic (Modern Standard)
* `zh_Hans`: Chinese (Simplified)
* `zh_Hant`: Chinese (Traditional)

## Translating

To translate the bot, you need to know the YAML and Discord flavored Markdown
syntax, this will help you to translate the bot. You can learn YAML syntax from
[here](https://learnxinyminutes.com/docs/yaml/) and general Markdown syntax from
[here](https://learnxinyminutes.com/docs/markdown/) then you can learn Discord
flavored Markdown syntax from [here](https://www.markdownguide.org/tools/discord/).

If you know YAML and Markdown already, there's a few things you need to know
before translating the bot:

* Do not create a JSON file, this will be automatically generated to JSON during
  initial setup.
* Any word inside `{CURLYBRACKET}` should not be translated. For example:
  `{USERNAME}` should not be translated to `{NAMAPENGGUNA}`, this will break
  Python properly format the strings
* Respect with Markdown syntaxes applied to original languages (`en_US` and
  `id_ID`). You must not apply formatting syntax other than what the sources
  used. For example:

  ```markdown
  **This** is **bold** text
  ```

  You should format the text as if, but not like this:

  ```markdown
  **This is bold text**
  ```

  This is to ensure uniformity in the bot's messages.
* Properly format your YAML file so it also respect 80 chars in your editor.
* Do not translate the `i18n\en_US.yaml` file, this is the default language

## Authoring

To author your translation, configure `meta` section in your translation file,
and put your GitHub username to `contributors` array.

Then, you must repeat this process on `_index.yaml`, also you may need to set
language `status` to `final`.

## Testing

To test your translation, you can set up default language (`LANGUAGE_CODE`) in
`.env` file to your language code. For example, if you want to test your
translation in `id_ID.yaml`, you can set `LANGUAGE_CODE` to `id_ID`.

Then, run the bot using `python main.py` command. Ensure that you've invoked
the commands you've translated, and check if the bot replies with your
translation.

## Submitting

Once you've finished translating the bot, you can submit your translation by
creating a pull request to this repository. Please ensure that you've tested
your translation before submitting.
