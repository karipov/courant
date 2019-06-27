# Interface Documentation
Here you will find information on how the bot is structured visually. This
mainly concerns the [`replies.json`](replies.json) file at the moment.


## Structure & Logic
The top-level keys (in caps), divide the responses of the bot across many
handlers, or "**sections**". Further down the tree, within each section, you may
find responses to certain commands, or error responses. These are themselves
dictionaries - and their contents are the **appropriate responses for different
languages**.

The FSM section, however, is more special, as it contains not just response
text, but **also keyboard and callback data** information. The callback data
is divided in a logical way, that must be respected throughout the document,
which is:

```
<type of callback data; default 'fsm'> : <future state> : <additional info>
```


## For Translators
You must **ignore** (as in don't touch):

- the HTML formatting tags, such as, but not limited to: `<a href="">`,
`<i>`, `</i>` and others, but make sure they stay intace as you are translating
- the `payload` key and its values
- the `TREE` key and its values

If you've noticed that your language code does not appear with an empty key in 
all of the responses, i.e. if it doesn't look like below:

```json
...
"start": {
    "en": "Hello there! Please select your language:",
    "your_language_code": ""
},
...
```

Then please contact [@tgcode](https://t.me/tgcode).