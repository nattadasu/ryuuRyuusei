# Genre & Themes/Tags Relinking

## Wot zis?

This is a collection of JSON that will relink all the genres and themes/tags in
the database to the new ones when applicable.

This to ensure that the genres and themes/tags are consistent across the
platforms, and avoid internationalizaton/localization duplication.

## Which one got affected?

The relinking will affects:

* MyAnimeList's Genres and Themes
* AniList's Genres and Tags
* SIMKL's Genres

## How does this work?

The JSON files are named after the genre/themes/tags that got affected, and the
value will contains new identification so it can be reapplied to proper one.

In Python, it was simply done by:

```python
import json
from slugify import slugify

from classes.jikan import JikanApi

def get_anime(media_id: int) -> dict:
  # Fetch anime from Jikan API
  with JikanApi() as jikan:
    anime = return jikan.get_anime(media_id)
  # Load i18n and link JSON
  with open(f"i18n/en_US.json", "r", encoding="utf-8") as f:
    i18n = json.load(f)
  with open(f"link/mal.json", "r", encoding="utf-8") as f:
    link = json.load(f)

  # Relink genres and themes/tags
  for g in anime["genres"]:
    try:
      s = slugify(g["name"], separator="_")
      l = link[s]
      i = i18n["genres"][l]
      g["name"] = i
    except KeyError:
      pass
  for t in anime["themes"]:
    try:
      s = slugify(t["name"], separator="_")
      l = link[s]
      i = i18n["themes"][l]
      t["name"] = i
    except KeyError:
      pass

  print(anime)
```
