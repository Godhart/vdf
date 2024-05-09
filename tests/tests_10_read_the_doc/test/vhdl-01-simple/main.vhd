-- NOTE: it's ad-hoc example of reverse VDF idea
-- Docs and VDF cells are burried into source file
-- Line with `%%vdf-reverse ` magic sequence marks it's reverse vdf format
-- word after magic sequence defines format for doc cells / output document
-- Sequence before `%%vdf-reverse ` defines start sequence to determine VDF data
-- Consequent lines with start sequence are treated as single cell
-- Ending fenced sequence is not necessary for code cells
-- First cell's line identation defines indent for generated code (if there would be any)

--- %%vdf-reverse markdown

--- ---
--- # Front matter part (due to extra --- above), YAML format
--- author: Nikolay Gniteev (godhart@gmail.com)
--- description: |-
---   Exmaple of description in source file (aka reverse VDF)
---   Showed approach allows to
---   - generate documents out of source
---   - generate code and documents from data in outer format
---   and keep them in sync
---
---   > NOTE: Shown below VDF tags just for example to illustrate idea
--    > and do not exitst/supported at time this file were created
--- version: 1.0.0

--- # Heading 1
---
--- Some text here

library library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

--- # Heading 2
---
--- Some text here too
---
--- For example - entity brief

entity main is
    generic (
        --- ```yaml
--- %%vdf generics
--- generics description in YAML format or ref to outer file

-- NOTE: after section above a generated code with generics should arise
    );
    port (
        --- ```yaml
--- %%vdf interface attr-prefix-xxx attr-suffix-yyy
--- regs description in YAML format or ref to outer file

-- NOTE: after section above a generated code with interfaces should arise
    );
end entity main;

--- # Heading 3
---
--- Some text here too

architecture rtl of main is

    --- ```rdml
--- %%vdf rdml
--- regs description in RDML format or ref to outer file

-- NOTE: after section above a generated code with registers definitions should arise

begin



end architecture rtl;
