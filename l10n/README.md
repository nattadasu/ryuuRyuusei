# Localization Guide

Hello and thank you for your interest to translating this bot! This guide will
help you to get started with translating the bot.

For your information, the bot is only officially supported in 2 languages:
English and Indonesian. However, you can still translate the bot to your
language if you want to.

All translations must be saved as Fluent (`*.ftl`) file, and must be placed in
the `l10n` directory. The file name must be in the format of
`<lang><_<script>><region>/main.ftl`, where:

* `<lang>` is the language code, in lowercase. For example: `en` for English,
  `id` for Indonesian, `zh` for Chinese, etc.
* `<_<script>>`, if present, is the script code, in lowercase. For example:
  `zh_hans` for Simplified Chinese, `zh_hant` for Traditional Chinese, etc.
* `<region>`, is 2-3 alphanumerical region code, in uppercase. For example:
  `US` for United States, `GB` for Great Britain, etc.
* and `main.ftl` is the file name.

Exclusion only applies to following:

* `ar_001`: Arabic (Modern Standard)
* `zh_Hans`: Chinese (Simplified)
* `zh_Hant`: Chinese (Traditional)

## Translating

To translate the bot, you need to know the Fluent syntax. Fluent is a
localization syntax developed by Mozilla, and is used in Firefox and other
Mozilla products. You can learn more about Fluent in
[its documentation](https://projectfluent.org/).

> **Warning**
>
> Do not translate the `i18n\en_US.yaml` file, this is the default language

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
