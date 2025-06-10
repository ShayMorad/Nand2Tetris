"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.class_table: dict[str, tuple[str, str, int]] = dict()
        self.subroutine_table: dict[str, tuple[str, str, int]] = dict()
        self.field_counter = 0
        self.static_counter = 0
        self.arg_counter = 0
        self.var_counter = 0

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.subroutine_table = dict()
        self.arg_counter = 0
        self.var_counter = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        if (kind in ["FIELD", "STATIC"]):
            if kind == "FIELD":
                self.class_table[name] = (type, kind, self.field_counter)
                self.field_counter += 1
            elif kind == "STATIC":
                self.class_table[name] = (type, kind, self.static_counter)
                self.static_counter += 1
        elif (kind in ["ARG", "VAR"]):
            if kind == "ARG":
                self.subroutine_table[name] = (type, kind, self.arg_counter)
                self.arg_counter += 1
            elif kind == "VAR":
                self.subroutine_table[name] = (type, kind, self.var_counter)
                self.var_counter += 1

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        if kind == "STATIC":
            return self.static_counter
        if kind == "FIELD":
            return self.field_counter
        if kind == "ARG":
            return self.arg_counter
        if kind == "VAR":
            return self.var_counter

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        if name in self.subroutine_table.keys():
            return self.subroutine_table[name][1]
        if name in self.class_table.keys():
            return self.class_table[name][1]

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if name in self.subroutine_table.keys():
            return self.subroutine_table[name][0]
        if name in self.class_table.keys():
            return self.class_table[name][0]

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if name in self.subroutine_table.keys():
            return self.subroutine_table[name][2]
        if name in self.class_table.keys():
            return self.class_table[name][2]

    def print_for_tests(self):
        for item in self.class_table.items():
            print(item[0], item[1])
        for item in self.subroutine_table.items():
            print(item[0], item[1])



if "__main__" == __name__:
    symboltable = SymbolTable()
    symboltable.define("x", "int", "FIELD")
    symboltable.define("y", "int", "FIELD")
    symboltable.define("z", "int", "FIELD")
    symboltable.define("a", "int", "STATIC")
    symboltable.define("arg0", "int", "ARG")
    symboltable.define("arg1", "int", "ARG")
    symboltable.define("var0", "Point", "VAR")
    symboltable.define("var1", "Point", "VAR")
    symboltable.print_for_tests()
    print(symboltable.var_count("FIELD"))
    print(symboltable.var_count("STATIC"))
    print(symboltable.var_count("ARG"))
    print(symboltable.var_count("VAR"))
    print("KIND OF arg0:",symboltable.kind_of("arg0"))
    print("INDEX OF var1:",symboltable.index_of( "var1"))
    print("TYPE OF var0: ",symboltable.type_of( "var0"))


    print("RESETTING SUBROUTINE TABLE....")
    symboltable.start_subroutine()
    symboltable.print_for_tests()
    print(symboltable.var_count("FIELD"))
    print(symboltable.var_count("STATIC"))
    print(symboltable.var_count("ARG"))
    print(symboltable.var_count("VAR"))


