---
# Frontmatter part:

title       : Simple Markdown-VHDL VDF example
author      : Nikolay Gniteev (godhart@gmail.com)
version     : "1.0.1"
vdf         : "1.0"

---

# Simple example with VHDL code

---

A header part that would be added before entity

```vhdl
%%vdf #header
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
```

---

Let's define clock


```vhdl
%%vdf #code
signal clk : std_logic := '0';
---
clk <= not clk after 5 ns;
```

---

Let's define some data signals

```vhdl
%%vdf #code-declaration
signal v1 : unsigned(7 downto 0) := x"05";
signal v2 : unsigned(7 downto 0) := x"07";
```

---

Lets define a function

```vhdl
%%vdf #code-declaration
function sum(a,b,c,d,e,f:unsigned(7 downto 0):=(others => '0')) return unsigned is
begin
    return a+b+c+d+e+f;
end function;
```

---

Now let's define one more signal

It's value would be defined by result of sum function, running every clk period

> (it's accumulator by the way)

```vhdl
%%vdf \
#code
signal s : unsigned(7 downto 0) := x"00";
---
s <= sum(s,v1,v2) when rising_edge(clk);
```

---
