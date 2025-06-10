"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import *


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = input_stream
        self.output = output_stream
        self.compilation_depth = 0
        self.TAB = "  "
        # output_stream.write("Hello world! \n")

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("class", True, "\n")
        self.compilation_depth += 1

        # print class keyword
        self._write_keyword(self.tokenizer.keyword().lower())
        self.tokenizer.advance()

        # print class name
        self._write_identifier(self.tokenizer.identifier())
        self.tokenizer.advance()

        # "{"
        self._write_symbol(self.tokenizer.symbol())
        self.tokenizer.advance()

        if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == '}'):
            self._write_symbol(self.tokenizer.symbol())
            self.tokenizer.advance()

        # else:
        #
        #     while ((self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() in ['STATIC', 'FIELD'])):
        #         self.compile_class_var_dec()
        #
        #     while ((self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() in ['CONSTRUCTOR',
        #                                                                                       'FUNCTION', 'METHOD'])):
        #         print(self.tokenizer.token_type(), self.tokenizer.keyword())
        #         self.compile_subroutine()
        #
        #     # "}"
        #     self._write_symbol(self.tokenizer.symbol())
        #     self.tokenizer.advance()

        else:
            while (not (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == '}')):
                if (self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() in ['STATIC', 'FIELD']):
                    self.compile_class_var_dec()
                elif (self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() in ['CONSTRUCTOR',
                                                                                                'FUNCTION', 'METHOD']):
                    self.compile_subroutine()

            # "}"
            self._write_symbol(self.tokenizer.symbol())
            self.tokenizer.advance()

        self.compilation_depth -= 1
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("class", False, "\n")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("classVarDec", True, "\n")
        self.compilation_depth += 1

        # print 'static' or 'field'
        self._write_keyword(self.tokenizer.keyword().lower())
        self.tokenizer.advance()

        # print if the type is int/char/boolean
        if (self.tokenizer.token_type() == "KEYWORD" and (self.tokenizer.keyword() in ["INT", "CHAR", "BOOLEAN"])):
            self._write_keyword(self.tokenizer.keyword().lower())
            self.tokenizer.advance()

        # print if the type is className
        elif (self.tokenizer.token_type() == "IDENTIFIER"):
            self._write_identifier(self.tokenizer.identifier())
            self.tokenizer.advance()

        # print the identifier/var name
        self._write_identifier(self.tokenizer.identifier())
        self.tokenizer.advance()

        if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ';'):
            self._write_symbol(self.tokenizer.symbol())
            self.tokenizer.advance()

        else:
            while (not (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ';')):

                if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ","):
                    self._write_symbol(self.tokenizer.symbol())
                    self.tokenizer.advance()

                elif (self.tokenizer.token_type() == "IDENTIFIER"):
                    self._write_identifier(self.tokenizer.identifier())
                    self.tokenizer.advance()

            self._write_symbol(self.tokenizer.symbol())
            self.tokenizer.advance()

        self.compilation_depth -= 1
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("classVarDec", False, "\n")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("subroutineDec", True, "\n")
        self.compilation_depth += 1

        # print subroutine type (constructor/function/method)
        self._write_keyword(self.tokenizer.keyword().lower())
        self.tokenizer.advance()

        # print return type (int/char/bool/void/custom=className)
        if (self.tokenizer.token_type() == "KEYWORD" and (
                self.tokenizer.keyword() in ["INT", "CHAR", "BOOLEAN", "VOID"])):
            self._write_keyword(self.tokenizer.keyword().lower())
        elif (self.tokenizer.token_type() == "IDENTIFIER"):
            self._write_identifier(self.tokenizer.identifier())
        self.tokenizer.advance()

        # print subroutine name
        self._write_identifier(self.tokenizer.identifier())
        self.tokenizer.advance()

        # "("
        self._write_symbol(self.tokenizer.symbol())
        self.tokenizer.advance()
        # param list if has any
        self.compile_parameter_list()
        # ")"
        self._write_symbol(self.tokenizer.symbol())
        self.tokenizer.advance()

        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("subroutineBody", True, "\n")
        self.compilation_depth += 1

        # "{"
        self._write_symbol(self.tokenizer.symbol())
        self.tokenizer.advance()

        while (self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() == "VAR"):
            self.compile_var_dec()

        while (self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() in ['LET', 'DO', 'IF', 'WHILE',
                                                                                         'RETURN']):
            self.compile_statements()

        # while (not (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == "}")):
        #     if (self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() == "VAR"):
        #         self.compile_var_dec()
        #     elif (self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() in ['LET', 'DO', 'IF', 'WHILE',
        #                                                                                     'RETURN']):
        #         self.compile_statements()
        #     self.output.write(self.tokenizer.token_type())

        # "}"
        self._write_symbol(self.tokenizer.symbol())
        self.tokenizer.advance()

        self.compilation_depth -= 1
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("subroutineBody", False, "\n")

        self.compilation_depth -= 1
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("subroutineDec", False, "\n")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("parameterList", True, "\n")
        self.compilation_depth += 1

        if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ")"):
            self.compilation_depth -= 1
            self.output.write(self.compilation_depth * self.TAB)
            self._write_tag("parameterList", False, "\n")
            return

        else:
            while (not (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ")")):

                # print if the type is int/char/boolean
                if (self.tokenizer.token_type() == "KEYWORD" and (
                        self.tokenizer.keyword() in ["INT", "CHAR", "BOOLEAN"])):
                    self._write_keyword(self.tokenizer.keyword().lower())

                elif (self.tokenizer.token_type() == "IDENTIFIER"):
                    self._write_identifier(self.tokenizer.identifier())

                elif (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ","):
                    self._write_symbol(self.tokenizer.symbol())

                self.tokenizer.advance()

        self.compilation_depth -= 1
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("parameterList", False, "\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("varDec", True, "\n")
        self.compilation_depth += 1

        # print 'var'
        self._write_keyword(self.tokenizer.keyword().lower())
        self.tokenizer.advance()

        # print if the type is int/char/boolean
        if (self.tokenizer.token_type() == "KEYWORD" and (self.tokenizer.keyword() in ["INT", "CHAR", "BOOLEAN"])):
            self._write_keyword(self.tokenizer.keyword().lower())
            self.tokenizer.advance()

        # print if the type is className
        elif (self.tokenizer.token_type() == "IDENTIFIER"):
            self._write_identifier(self.tokenizer.identifier())
            self.tokenizer.advance()

        # print the identifier
        self._write_identifier(self.tokenizer.identifier())
        self.tokenizer.advance()

        if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ';'):
            self._write_symbol(self.tokenizer.symbol())
            self.tokenizer.advance()

        else:
            while (not (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ';')):

                if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ","):
                    self._write_symbol(self.tokenizer.symbol())
                    self.tokenizer.advance()

                elif (self.tokenizer.token_type() == "IDENTIFIER"):
                    self._write_identifier(self.tokenizer.identifier())
                    self.tokenizer.advance()
            self._write_symbol(self.tokenizer.symbol())
            self.tokenizer.advance()

        self.compilation_depth -= 1
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("varDec", False, "\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("statements", True, "\n")
        self.compilation_depth += 1

        while (self.tokenizer.token_type() == "KEYWORD" and (
                self.tokenizer.keyword() in ['LET', 'DO', 'IF', 'WHILE', 'RETURN'])):
            if (self.tokenizer.keyword() == "LET"):
                self.compile_let()
            elif (self.tokenizer.keyword() == "DO"):
                self.compile_do()
            elif (self.tokenizer.keyword() == "IF"):
                self.compile_if()
            elif (self.tokenizer.keyword() == "WHILE"):
                self.compile_while()
            elif (self.tokenizer.keyword() == "RETURN"):
                self.compile_return()

        self.compilation_depth -= 1
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("statements", False, "\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("doStatement", True, "\n")
        self.compilation_depth += 1
        # printing 'do'
        self._write_keyword(self.tokenizer.keyword().lower())
        self.tokenizer.advance()
        self._write_identifier(self.tokenizer.identifier())
        self.tokenizer.advance()

        if (self.tokenizer.symbol() == "."):
            self._write_symbol(self.tokenizer.symbol())
            self.tokenizer.advance()
            self._write_identifier(self.tokenizer.identifier())
            self.tokenizer.advance()
            self._write_symbol(self.tokenizer.symbol())
            self.tokenizer.advance()
            self.compile_expression_list()
            self._write_symbol(self.tokenizer.symbol())
            self.tokenizer.advance()

        elif (self.tokenizer.symbol() == "("):
            self._write_symbol(self.tokenizer.symbol())
            self.tokenizer.advance()
            self.compile_expression_list()
            self._write_symbol(self.tokenizer.symbol())
            self.tokenizer.advance()

        self._write_symbol(self.tokenizer.symbol())
        self.tokenizer.advance()

        self.compilation_depth -= 1
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("doStatement", False, "\n")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("letStatement", True, "\n")
        self.compilation_depth += 1

        # printing "let"
        self._write_keyword(self.tokenizer.keyword().lower())
        self.tokenizer.advance()

        # printing identifier
        self._write_identifier(self.tokenizer.identifier())
        self.tokenizer.advance()
        self._check_var_name()
        # printing "="
        self._write_symbol(self.tokenizer.symbol())
        self.tokenizer.advance()

        self.compile_expression()

        # printing ";"
        self._write_symbol(self.tokenizer.symbol())

        self.tokenizer.advance()
        self.compilation_depth -= 1
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("letStatement", False, "\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # 'while' '(' expression ')' '{' statements '}'
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("whileStatement", True, "\n")
        self.compilation_depth += 1

        # printint "while"
        self._write_keyword(self.tokenizer.keyword().lower())
        self.tokenizer.advance()

        # '('
        self._write_symbol(self.tokenizer.symbol())
        self.tokenizer.advance()

        # expression
        self.compile_expression()

        # ')'
        self._write_symbol(self.tokenizer.symbol())
        self.tokenizer.advance()

        # '{'
        self._write_symbol(self.tokenizer.symbol())
        self.tokenizer.advance()

        # statements
        self.compile_statements()

        # '}'
        self._write_symbol(self.tokenizer.symbol())
        self.tokenizer.advance()

        self.compilation_depth -= 1
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("whileStatement", False, "\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("returnStatement", True, "\n")
        self.compilation_depth += 1

        # printing "return"
        self._write_keyword(self.tokenizer.keyword().lower())
        self.tokenizer.advance()

        if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ";"):
            self._write_symbol(self.tokenizer.symbol())

        else:
            self.compile_expression()
            self._write_symbol(self.tokenizer.symbol())

        self.tokenizer.advance()
        self.compilation_depth -= 1
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("returnStatement", False, "\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""

        # 'if' '(' expression ')' '{' statements '}'  ( 'else' '{' statementes '}'  )?
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("ifStatement", True, "\n")
        self.compilation_depth += 1

        # printing "if"
        self._write_keyword(self.tokenizer.keyword().lower())
        self.tokenizer.advance()

        # '('
        self._write_symbol(self.tokenizer.symbol())
        self.tokenizer.advance()

        # expression
        self.compile_expression()

        # ')'
        self._write_symbol(self.tokenizer.symbol())
        self.tokenizer.advance()

        # '{'
        self._write_symbol(self.tokenizer.symbol())
        self.tokenizer.advance()

        # statements
        self.compile_statements()

        # '}'
        self._write_symbol(self.tokenizer.symbol())
        self.tokenizer.advance()

        if (self.tokenizer.token_type() == "KEYWORD"):
            if (self.tokenizer.keyword() == "ELSE"):
                # 'else'
                self._write_keyword(self.tokenizer.keyword().lower())
                self.tokenizer.advance()

                # '{'
                self._write_symbol(self.tokenizer.symbol())
                self.tokenizer.advance()

                # statements
                self.compile_statements()

                # '}'
                self._write_symbol(self.tokenizer.symbol())
                self.tokenizer.advance()

        self.compilation_depth -= 1
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("ifStatement", False, "\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("expression", True, "\n")
        self.compilation_depth += 1
        self.compile_term()

        # check if next token is an operator symbol and if so compile the next term
        while (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() in ['+', '-', '*', '/', '&', '|',
                                                                                       '<', '>', '=']):
            if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() in ['+', '-', '*', '/', '&', '|',
                                                                                        '<', '>', '=']):
                self._write_symbol(self.tokenizer.symbol())
                self.tokenizer.advance()
            self.compile_term()

        self.compilation_depth -= 1
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("expression", False, "\n")

    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("term", True, "\n")
        self.compilation_depth += 1

        prev_token_type = self.tokenizer.token_type()
        prev_token_symbol = self.tokenizer.symbol()

        if (self.tokenizer.token_type() == "INT_CONST"):
            self._write_integer_const(self.tokenizer.int_val())
            self.tokenizer.advance()

        elif (self.tokenizer.token_type() == "STRING_CONST"):
            self._write_string_const(self.tokenizer.string_val())
            self.tokenizer.advance()

        # can be only one of - ['true', 'false', 'null', 'this']
        elif (self.tokenizer.token_type() == "KEYWORD"):
            self._write_keyword(self.tokenizer.keyword().lower())
            self.tokenizer.advance()

        elif (self.tokenizer.token_type() == "IDENTIFIER"):
            self._write_identifier(self.tokenizer.identifier())
            self.tokenizer.advance()
            # if(self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ")"):
            #     self._write_symbol(self.tokenizer.symbol())
            self._check_var_name()

        # can be only one of - ['-', '~', '^', '#', '(']
        elif (self.tokenizer.token_type() == "SYMBOL"):
            self._write_symbol(self.tokenizer.symbol())
            self.tokenizer.advance()

            # if (self.tokenizer.symbol() == "("):
            #     self.tokenizer.advance()
            #     self.compile_expression()
            #
            #     self._write_symbol(self.tokenizer.symbol())
            #
            # elif (self.tokenizer.symbol() in ['-', '~', '^', '#']):
            #     self.tokenizer.advance()
            #     self.compile_term()

            # self.tokenizer.advance()

        if (prev_token_type == "SYMBOL" and prev_token_symbol == "("):
            self.compile_expression()
            self._write_symbol(self.tokenizer.symbol())
            self.tokenizer.advance()

        elif (prev_token_type == "SYMBOL" and prev_token_symbol in ['-', '~', '^', '#']):
            self.compile_term()

        self.compilation_depth -= 1
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("term", False, "\n")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("expressionList", True, "\n")
        self.compilation_depth += 1

        if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ")"):
            self.compilation_depth -= 1
            self.output.write(self.compilation_depth * self.TAB)
            self._write_tag("expressionList", False, "\n")
            return

        else:
            while (not (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ")")):
                self.compile_expression()
                if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ","):
                    self._write_symbol(self.tokenizer.symbol())
                    self.tokenizer.advance()

        self.compilation_depth -= 1
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("expressionList", False, "\n")

    def _write_tag(self, text, is_open, new_line):
        if (is_open is True):
            if(text in ["keyword", "identifier", "symbol", "integerConstant", "stringConstant", ]):
                self.output.write("<" + text + "> " + new_line)
            else:
                self.output.write("<" + text + ">" + new_line)
        else:
            self.output.write("</" + text + ">" + new_line)

    def _write_keyword(self, text):
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("keyword", True, "")
        self.output.write(text + " ")
        self._write_tag("keyword", False, "\n")

    def _write_symbol(self, symbol):
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("symbol", True, "")

        if (symbol in ["<", ">", "&"]):
            if (symbol == "<"):
                symbol = "&lt;"
            elif (symbol == ">"):
                symbol = "&gt;"
            elif (symbol == "&"):
                symbol = "&amp;"

        self.output.write(symbol + " ")
        self._write_tag("symbol", False, "\n")

    def _write_integer_const(self, integer):
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("integerConstant", True, "")
        self.output.write(str(integer) + " ")
        self._write_tag("integerConstant", False, "\n")

    def _write_string_const(self, string):
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("stringConstant", True, "")
        self.output.write(string + " ")
        self._write_tag("stringConstant", False, "\n")

    def _write_identifier(self, identifier):
        self.output.write(self.compilation_depth * self.TAB)
        self._write_tag("identifier", True, "")
        self.output.write(identifier + " ")
        self._write_tag("identifier", False, "\n")

    def _check_var_name(self):
        if (self.tokenizer.token_type() == "SYMBOL"):
            if (self.tokenizer.symbol() == "["):
                self._write_symbol(self.tokenizer.symbol())
                self.tokenizer.advance()
                self.compile_expression()
                self._write_symbol(self.tokenizer.symbol())
                self.tokenizer.advance()

            elif (self.tokenizer.symbol() == "."):
                self._write_symbol(self.tokenizer.symbol())
                self.tokenizer.advance()
                self._write_identifier(self.tokenizer.identifier())
                self.tokenizer.advance()
                # "("
                self._write_symbol(self.tokenizer.symbol())
                self.tokenizer.advance()
                self.compile_expression_list()
                self._write_symbol(self.tokenizer.symbol())
                self.tokenizer.advance()

            elif (self.tokenizer.symbol() == "("):
                self._write_symbol(self.tokenizer.symbol())
                self.tokenizer.advance()
                self.compile_expression_list()
                self._write_symbol(self.tokenizer.symbol())
                self.tokenizer.advance()
