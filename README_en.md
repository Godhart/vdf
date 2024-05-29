# VDF - Versatile Description Format

![main build](https://github.com/Godhart/vdf/actions/workflows/python-app.yml/badge.svg)

![intro](https://imgs.xkcd.com/comics/standards.png)

# Idea

Let's not compete! Just embrace them all!

Mix doc and code and use whatever you want (or so)

Ok. But you still need one more standard for this...

For details - check [spec](https://github.com/Godhart/vdf/blob/main/spec/vdf_specification_en.md):

Here is a short [example](https://github.com/Godhart/vdf/blob/main/examples/jl-simple/hello-world.ipynb) how it may look like

# Current state

Specification declaration is at draft state - things may change without backward compatibility, a lot to think about and to check.

Specification core is implemented at minimal level for proof-of-concept and ideas evaluation.

First specification use is designated for HDL languages like VHDL, Verilog etc. but it can be applied to any coding language (and even more)

Check [roadmap](https://github.com/Godhart/vdf/blob/main/ROADMAP_en.md) for details.

> Just found out that [Quarto](https://quarto.org) have implemented many ideas behind this project. VDF approach would be reconsidered in respect to Quarto.

# Contribution

Contributions are appreciated.

Way of contribution is not defined yet but will be soon.

Preferred area for contributions is defined [here](https://github.com/Godhart/vdf/blob/main/TODO_en.md).

# Used software/techs stack

## Core

- Python
- Jupyter
- JSON
- YAML
- TOML
- Jinja2
<!--
TODO:
- Pandoc
-->

## Structured text

- Markdown
- to be continued...

## RTL tools

- GHDL
<!-- - #TODO: Verilator -->
<!-- - #TODO: Icarus -->
- Cocotb
- to be continued...

<!--
TODO:
- wavedrom
- hdelk
- yaml4hdelk
-->
