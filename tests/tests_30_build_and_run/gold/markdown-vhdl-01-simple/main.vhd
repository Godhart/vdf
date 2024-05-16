library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity main is
end entity;


architecture rtl of main is

    signal clk : std_logic := '0';
    signal v1 : unsigned(7 downto 0) := x"05";
    signal v2 : unsigned(7 downto 0) := x"07";
    function sum(a,b,c,d,e,f:unsigned(7 downto 0):=(others => '0')) return unsigned is
    begin
        return a+b+c+d+e+f;
    end function;
    signal s : unsigned(7 downto 0) := x"00";

begin

    clk <= not clk after 5 ns;
    s <= sum(s,v1,v2) when rising_edge(clk);

end architecture;