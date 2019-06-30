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

Additionally, it also contains a **hierarchal tree structure** of it's states
and how they are related to each other. It's parsed using the
[anytree](https://github.com/c0fec0de/anytree) library, and looks something
like this:

```json
"TREE": {
    "name": "1",
    "children": [
        {
            "name": "2",
            "children": [
                {
                    "name": "2.1",
                    "children": [
...
```

The tree structure is used in the `check_fsm(...)` function found in
[`utility.py`](../utility.py).


## For Translators
You must **ignore** (as in *don't touch*):

- HTML formatting tags, such as, but not limited to: `<a href="">`,
`<i>`, `</i>` and others; however, make sure they **stay intact** as you are
translating
- `FSM/[state]/payload` key and its value(s)
- `FSM/TREE` key and its value(s)

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