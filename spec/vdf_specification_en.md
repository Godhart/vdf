---
#var-frontmatter #format-yaml

title       : Versatile Description Format specification
author      : Nikolay Gniteev (godhart@gmail.com)
version     : 1.0.draft.4
description : Specification of Versatile Description Format (for hardware)

---

# Versatile Description Format Specification

This format provides a mixed description of documentation and code in one file

The format allows you to combine different structured text description formats, languages and description methods in one file

The format allows you to describe documentation and code in sections and keep the description and code next to each other, as well as generate code fragments from the description itself

From the file described in this format, you can obtain documentation and source files. Also using a description in this format allows for interactive execution / incremental compilation of code, etc.

The format allows you to create documentation, code and related artifacts and interactively execute code by sequentially adding/changing fragments of documentation and code using “cells”, which are the main “building” element of the document

Chains of document cells can be organized in both linear and non-linear ways to clearly show the difference between different options or to conduct experiments

#TODO: will be translated as some things in original would be settled down

> Just found out that [Quarto](https://quarto.org) have implemented many ideas behind this project. VDF approach would be reconsidered in respect to Quarto.
