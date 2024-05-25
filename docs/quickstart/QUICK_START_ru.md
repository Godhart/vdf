# Инструкция по быстрому старту

## Локальный запуск

Этот вариант предназначен для запуска непосредственно на вашей ПЭВМ

Локальный запуск рекомендуется использовать только для разработки, т.к. выполнение документов из недоверенных источников опасно.

Для остальных случаев рекомендуется запуск в контейнере docker или в облаке (эти варианты пока в проработке, будут добавлены в инструкцию очень скоро).

### Требования к системе

Успех локального запуска будет зависеть от того какая ОС и версия пакетов используется на хосте. При разработке была использована следующая конфигурация системы:

- OS: Linux
- Python: 3.11.8
- GHDL: 4.1.0
- Перечень пакетов Python и использованный номер их версии указан в файле `requirements_f.txt`

> Известно что версия GHDL должна быть не ниже 2.x

### Установка

1. Установите интерпретатор Python и симулятор (на данный момент поддерживается только GHD)

2. Получите актуальную версию данного на репозитория на вашей ПЭВМ - склонируйте репозиторий используя git или скачайте в виде [архива](https://github.com/Godhart/vdf/archive/refs/heads/main.zip) и распакуйте в папку

```sh
git clone https://github.com/Godhart/vdf.git
```

3. Создайте виртуальное окружение Python (не обязательно но крайне настоятельно рекомендуется) внутри полученной папки (далее "корень рабочей папки")

```sh
python -m pip venv .venv
```

Каждый раз перед запуском, в командной оболочке не забывайте активировать виртуальное окружение из корня рабочей папки

```sh
source .venv/bin/activate
```

> Подробнее про виртуальные окружения можно почитать в [источнике](https://docs.python.org/3/tutorial/venv.html) и других статьях, если вы ещё об этом не знаете

4. Установите требуемые пакеты Python после создания виртуального окружения

```sh
python -m pip install -r requirements.txt
```

### Запуск

В корне рабочей папки активируйте виртуальное окружение и запустите Jupyter

#### в режиме одного документа (Notebook)

```sh
jupyter notebook
```
#### в режиме одного документа (Notebook)

```sh
jupyter lab
```

Запущенная среда Jupyter будет доступна в web-браузере по пути [http://localhost:8888](http://localhost:8888)

Создавайте и работайте с документами. Корнем каталогов в среде Jupyter будет корень рабочей папки.

> Это можно изменить через параметры [запуска](https://docs.jupyter.org/en/latest/running.html)

Можете для начала открыть и попробовать примеры из `examples/jl-simple`