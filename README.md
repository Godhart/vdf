# VDF - Versatile Description Format aka Универсальный Формат Описания

![main build](https://github.com/Godhart/vdf/actions/workflows/python-app.yml/badge.svg)

![intro](https://imgs.xkcd.com/comics/standards.png)

# Идея данного проекта

Не надо создавать новый стандарт! Просто совмести те, что уже есть!

Объединяй описание и код в одном документе и используй для этого тот формат, который ты хочешь (или что-то вроде)

Хорошо. Но тебе всё же понадобится ещё один стандарт для этого...

Более подробные детали данной идеи можно посмотреть в [черновике спецификации](https://github.com/Godhart/vdf/blob/main/spec/vdf_specification_ru.md)

Вот небольшой [пример](https://github.com/Godhart/vdf/blob/main/examples/jl-simple/hello-world-ru.ipynb) того как это могло бы выглядеть.

# Специально для читателей FSM

Дополнительную информацию к статье в журнале (ссылки и т.п.) можно посмотреть на [этой](https://github.com/Godhart/vdf/blob/main/docs/fsm/APPENDIX_ru.md) странице

# Текущее состояние проекта

Имеется спецификация на уровне черновика. Многие вещи пока что ещё могут изменяться без обратной совместимости. Есть ещё много над чем подумать и что проверить.

По этой спецификации уже реализовано ядро системы на уровне, достаточном для проверки гипотез и предварительной оценки.

Первая цель применения данной спецификации - языки описания аппаратуры, тике как VHDL, Verilog. Но в целом спецификация позволяет расширять её применение и на другие языки программирования.

На текущем уровне реализации уже можно выполнять интерактивный ввод исходного файла на языке VHDL и его симуляцию.

Чтобы ознакомиться на практике с текущими возможностями воспользуйтесь [этим](https://github.com/Godhart/vdf/blob/main/docs/quickstart/QUICK_START_ru.md) руководством.

Направление планов по развитию проекта можно посмотреть в этой [дорожной карте](https://github.com/Godhart/vdf/blob/main/ROADMAP_ru.md).

За анонсами проекта можно наблюдать в телеграм-канале [@vdfspec](https://t.me/vdfspec).

# Участие в проекте

Проект открытый и участие в нём приветствуется.

Проект пока ещё очень молод и общая стратегия для участия в нём пока не определена, но при желании вы можете в частном порядке связаться с автором по почте [godhart@gmail.com](mailto:godhart@gmail.com) или телеграм [@Godhart](https://t.me/Godhart) и обговорить детали участия.

# Какие технологии используются в проекте

## Ядро системы

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

## Форматы описания

- Markdown
- и в планах поддержать больше ...

## RTL инструментарий

- GHDL
- Cocotb
- wavedrom
- и в планах поддержать больше ...

<!-- - #TODO: Verilator -->
<!-- - #TODO: Icarus -->

<!--
TODO:
- hdelk
- yaml4hdelk
-->
