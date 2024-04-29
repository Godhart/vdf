---
# Frontmatter part:

title       : Simple test for markdown input
author      : Nikolay Gniteev (godhart@gmail.com)
version     : "1.0"
vdf         : "1.0"   # Используемая спецификация

---

# First header

test section

---

```vhdl
%%vdf #code

---

```

---

# Second header

text goes here

```vhdl
%%vdf #code #kind header

---

```

moar text here

```vhdl
%%vdf #code #kind package

---

```

and a bit more text