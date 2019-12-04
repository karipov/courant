# Interface Documentation
Here you will find information on how the bot is structured visually. This
mainly concerns the [`replies.json`](replies.json) file at the moment.


## Structure & Logic
The top-level keys (in caps), divide the responses of the bot across many
handlers, or "**sections**". Further down the tree, within each section, you may
find responses to certain commands, or error responses. These are themselves
dictionaries - and their contents are the **appropriate responses for different languages**.

One also may notice the special FSM top-level key, within which are seen the
FSM states themselves, indicated as numbers separated by dots. Within those, 
you will find the `text` and `markup` key which contains a dictionary of 
responses separated by different iso language codes:

```json
"num.num.num" : {
    "text": {
        "lang_code_iso": text in lang,
        "another_lang_code_iso": text in another lang
    },
    "markup": {
        "lang_code_iso": markup in lang,
        "another_lang_code_iso": markup in another lang
    }
}
```

Additionally, it also contains another key: `payload`. This key must not be
touched or modified for the purposes of translation, as it's only useful for
controlling the logic of the bot.

## For Translators
You must **ignore** (as in *don't touch*):

- HTML formatting tags, such as, but not limited to: `<a href="">`,
`<i>`, `</i>` and others; however, make sure they **stay intact** as you are
translating
- `FSM/[state]/payload` key and its value(s)

Furthermore, if you've noticed that your language code does not appear with an
empty key in all of the responses, i.e. if it doesn't look like below:

```json
...
"start": {
    "en": "Hello there! Please select your language:",
    "your_language_code": ""
},
...
```

Then please contact [@tgcode](https://t.me/tgcode).