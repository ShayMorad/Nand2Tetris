"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import *
from VMWriter import *
from SymbolTable import *


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", vmwriter: VMWriter) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = input_stream
        self.vmwriter = vmwriter  # we write using the VMWriter instead of directly into the output file unlike project 10
        self.symbol_table = SymbolTable()
        self.class_tag = ""  # for the sake of working inside a class
        self.subroutine_id = 0  # for differentianting different subroutine calls

        self.un_operators_to_word = {
            "-": "NEG",
            "~": "NOT",
            "^": "SHIFTLEFT",
            "#": "SHIFTRIGHT",
        }

        self.bi_operators_to_word = {
            "+": "ADD",
            "-": "SUB",
            "=": "EQ",
            ">": "GT",
            "<": "LT",
            "&": "AND",
            "|": "OR",
            "*": "Math.multiply",
            "/": "Math.divide"
        }


    def compile_class(self) -> None: #### DONE
        """Compiles a complete class."""
        # class
        self.tokenizer.advance()
        ##print("class name ", self.tokenizer.token())
        self.class_tag = self.tokenizer.identifier()

        # class name
        self.tokenizer.advance()
        # '{'
        ##print("{ ", self.tokenizer.token())
        self.tokenizer.advance()

        if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == '}'):
            self.tokenizer.advance()
            return

        else:
            while (not (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == '}')):
                if (self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() in ['STATIC', 'FIELD']):
                    self.compile_class_var_dec()
                elif (self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() in ['CONSTRUCTOR',
                                                                                                'FUNCTION', 'METHOD']):
                    self.compile_subroutine()

            # "}"
            ##print("{ ", self.tokenizer.token())
            self.tokenizer.advance()

    def compile_class_var_dec(self) -> None:  ######## DONE
        """Compiles a static declaration or a field declaration."""

        # 'static' or 'field'
        ##print("static or field", self.tokenizer.token())
        var_kind = self.tokenizer.keyword()
        self.tokenizer.advance()
        var_type = None
        # int/char/boolean
        ##print("int char bool: ", self.tokenizer.token())
        if (self.tokenizer.token_type() == "KEYWORD" and (self.tokenizer.keyword() in ["INT", "CHAR", "BOOLEAN"])):
            var_type = self.tokenizer.keyword()
            self.tokenizer.advance()

        # className
        elif (self.tokenizer.token_type() == "IDENTIFIER"):
            ##print("classname: ", self.tokenizer.token())
            var_type = self.tokenizer.identifier()
            self.tokenizer.advance()

        # handle 1st identifier
        ##print("var name:  ", self.tokenizer.token())
        self.symbol_table.define(self.tokenizer.identifier(), var_type, var_kind)
        self.tokenizer.advance()

        if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ';'):
            self.tokenizer.advance()

        else:
            while (not (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ';')):
                ##print("class var dec")

                if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ","):
                    self.tokenizer.advance()

                elif (self.tokenizer.token_type() == "IDENTIFIER"):
                    ##print("var name: ", self.tokenizer.token())
                    self.symbol_table.define(self.tokenizer.identifier(), var_type, var_kind)
                    self.tokenizer.advance()
            self.tokenizer.advance()

    def compile_subroutine(self) -> None:  ##### DONE
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """

        subroutine_type = self.tokenizer.keyword()
        ##print("subroutine TYPE: ", self.tokenizer.token())
        self.symbol_table.start_subroutine()

        # (constructor/function/method)
        if subroutine_type == "METHOD":
            self.symbol_table.define("THIS", self.class_tag, "ARG")

        self.tokenizer.advance()

        # subroutine return type
        ##print("subroutine return type ", self.tokenizer.token())
        self.tokenizer.advance()

        # subroutine name
        subroutine_name = self.tokenizer.identifier()
        ##print("subroutine name ", self.tokenizer.token())
        self.tokenizer.advance()

        # "("
        ##print("(", self.tokenizer.token())
        self.tokenizer.advance()
        # param list if has any
        self.compile_parameter_list()
        # ")"
        ##print(")", self.tokenizer.token())
        self.tokenizer.advance()

        # "{"
        ##print("{", self.tokenizer.token())
        self.tokenizer.advance()
        ##print("VAR or STATEMENTS", self.tokenizer.token())
        while (self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() == "VAR"):
            ##print("compiling var dec")
            self.compile_var_dec()


        ##print(self.symbol_table.var_count("ARG"))

        self.vmwriter.write_function(self.class_tag + "." + subroutine_name, self.symbol_table.var_count("VAR"))

        if subroutine_type == "METHOD":
            self.vmwriter.write_push("ARGUMENT", 0)
            self.vmwriter.write_pop("POINTER", 0)

        elif subroutine_type == "CONSTRUCTOR":
            self.vmwriter.write_push("CONSTANT", self.symbol_table.var_count("FIELD"))
            self.vmwriter.write_call("Memory.alloc", 1)
            self.vmwriter.write_pop("POINTER", 0)


        while (self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() in ['LET', 'DO', 'IF', 'WHILE',
                                                                                         'RETURN']):
            ##print("compiling statements")
            self.compile_statements()

        #print("token at end of compile subroutine: ", self.tokenizer.token())
        self.tokenizer.advance()

    def compile_parameter_list(self) -> None: #### DONE
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """


        if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ")"):
            return

        else:
            while (not (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ")")):
                #print("param list")
                if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ","):
                    self.tokenizer.advance()

                var_type = None

                # int/char/boolean
                if (self.tokenizer.token_type() == "KEYWORD" and (
                        self.tokenizer.keyword() in ["INT", "CHAR", "BOOLEAN"])):
                    var_type = self.tokenizer.keyword()
                    self.tokenizer.advance()

                # className
                elif (self.tokenizer.token_type() == "IDENTIFIER"):
                    #print("class name: ", self.tokenizer.token())
                    var_type = self.tokenizer.identifier()
                    self.tokenizer.advance()

                self.symbol_table.define(self.tokenizer.identifier(), var_type, "ARG")
                self.tokenizer.advance()

    def compile_var_dec(self) -> None:   ##### DONE
        """Compiles a var declaration."""


        #'var'
        #print("var: ", self.tokenizer.token())
        self.tokenizer.advance()

        var_type = None

        # int/char/boolean
        #print("int char bool or class name", self.tokenizer.token())
        if (self.tokenizer.token_type() == "KEYWORD" and (self.tokenizer.keyword() in ["INT", "CHAR", "BOOLEAN"])):
            var_type = self.tokenizer.keyword()

        # else var is of type className
        elif (self.tokenizer.token_type() == "IDENTIFIER"):
            var_type = self.tokenizer.identifier()

        self.tokenizer.advance()

        # handle 1st identifier
        #print("var name:  ", self.tokenizer.token())
        self.symbol_table.define(self.tokenizer.identifier(), var_type, "VAR")
        self.tokenizer.advance()

        if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ';'):
            self.tokenizer.advance()

        else:
            while (not (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ';')):
                #print("var dec")
                if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ","):
                    self.tokenizer.advance()

                elif (self.tokenizer.token_type() == "IDENTIFIER"):
                    #print("var name: ", self.tokenizer.token())
                    self.symbol_table.define(self.tokenizer.identifier(), var_type, "VAR")
                    self.tokenizer.advance()
            #print(";", self.tokenizer.token())
            self.tokenizer.advance()

    def compile_statements(self) -> None: ##### DONE
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """

        #print("keyword: let do if while return - ", self.tokenizer.token())
        while (self.tokenizer.token_type() == "KEYWORD" and (
                self.tokenizer.keyword() in ['LET', 'DO', 'IF', 'WHILE', 'RETURN'])):
            #print("statements")
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

    def compile_do(self) -> None: #### DONE
        """Compiles a do statement."""
        # 'do'
        #print("do :", self.tokenizer.token())
        self.tokenizer.advance()

        function = ""
        args = 0
        while self.tokenizer.symbol() != "(":
            #print("do")
            if self.tokenizer.token_type() == "KEYWORD":
                #print("ERROR IN COMPILE_DO")
                pass

            elif self.tokenizer.token_type() == "SYMBOL":
                #print("symbol for function name: ", self.tokenizer.token())
                function += self.tokenizer.symbol()

            elif self.tokenizer.token_type() == "IDENTIFIER":
                #print("identifier for function name: ", self.tokenizer.token())
                function += self.tokenizer.identifier()

            elif self.tokenizer.token_type() == "INT_CONST":
                #print("integer for function name: ", self.tokenizer.token())
                function += str(self.tokenizer.int_val())

            elif self.tokenizer.token_type() == "STRING_CONST":
                #print("string for function name: ", self.tokenizer.token())
                function += self.tokenizer.string_val()
            self.tokenizer.advance()

        #print("( :", self.tokenizer.token())
        self.tokenizer.advance()

        # must split because method call can be object.method() or method()
        if self.symbol_table.type_of(function.split('.')[0]) != None:
            #print("XXXXXXXX")
            args += 1

            var_name = function.split('.')[0]
            method_name = function.split('.')[1]
            #print("var_name: ", var_name)
            #print("method_name: ", method_name)
            var_type = self.symbol_table.type_of(var_name)
            var_kind = self.symbol_table.kind_of(var_name)
            var_index = self.symbol_table.index_of(var_name)
            #print("function = var_type+method_name: ", function)
            function = var_type + "." + method_name

            if var_kind == "FIELD":
                self.vmwriter.write_push("THIS", var_index)
            elif var_kind == "STATIC":
                self.vmwriter.write_push("STATIC", var_index)
            elif var_kind == "ARG":
                self.vmwriter.write_push("ARGUMENT", var_index)
            elif var_kind == "VAR":
                self.vmwriter.write_push("LOCAL", var_index)

        if '.' not in function:
            args += 1
            self.vmwriter.write_push("POINTER", 0)
            #print("function = class_tage + . + function: ", function)
            function = self.class_tag +"."+ function

        args += self.compile_expression_list()
        self.vmwriter.write_call(function, args)
        # ')'
        #print(")", self.tokenizer.token())
        self.tokenizer.advance()
        #print(";", self.tokenizer.token())
        # ';'
        self.tokenizer.advance()

        self.vmwriter.write_pop("TEMP", 0)

    def compile_let(self) -> None:  #### DONE
        """Compiles a let statement."""

        # "let"
        #print("let: ", self.tokenizer.token())
        self.tokenizer.advance()

        var_name = ""
        while self.tokenizer.token_type() != "SYMBOL":
            var_name += self.tokenizer.identifier()
            self.tokenizer.advance()
        #print("var name: ", var_name)
        var_index = self.symbol_table.index_of(var_name)
        var_kind = self.symbol_table.kind_of(var_name)
        #print("var index and var kind: ", var_index, var_kind)

        var_is_arr = False

        if self.tokenizer.symbol() == "[":
            var_is_arr = True


        if var_is_arr:
            #print("[: ", self.tokenizer.token())
            self.tokenizer.advance()

            self.compile_expression()  # here we pushed the item's index into the stack already
            #print("]: ", self.tokenizer.token())
            self.tokenizer.advance()
            if var_kind == "FIELD":
                self.vmwriter.write_push("THIS", var_index)
            elif var_kind == "STATIC":
                self.vmwriter.write_push("STATIC", var_index)
            elif var_kind == "ARG":
                self.vmwriter.write_push("ARGUMENT", var_index)
            elif var_kind == "VAR":
                self.vmwriter.write_push("LOCAL", var_index)

            self.vmwriter.write_arithmetic("ADD")  # add base array address + item's index

        # "="
        #print("=: ", self.tokenizer.token())
        self.tokenizer.advance()
        self.compile_expression()

        if var_is_arr:
            self.vmwriter.write_pop("TEMP", 0)
            self.vmwriter.write_pop("POINTER", 1)
            self.vmwriter.write_push("TEMP", 0)
            self.vmwriter.write_pop("THAT", 0)
        else:
            if var_kind == "FIELD":
                self.vmwriter.write_pop("THIS", var_index)
            elif var_kind == "STATIC":
                self.vmwriter.write_pop("STATIC", var_index)
            elif var_kind == "ARG":
                self.vmwriter.write_pop("ARGUMENT", var_index)
            elif var_kind == "VAR":
                self.vmwriter.write_pop("LOCAL", var_index)

        # ";"
        #print("; : ", self.tokenizer.token())
        self.tokenizer.advance()

    def compile_while(self) -> None:  ############ DONE
        """Compiles a while statement."""
        self.subroutine_id += 1
        cur_id = self.subroutine_id

        while self.tokenizer.symbol() != '(':
            #print("while")
            self.tokenizer.advance()
        self.vmwriter.write_label("WHILE_START." + str(cur_id))
        # '('
        self.tokenizer.advance()
        #print("identifier in while expression: ", self.tokenizer.token())
        # expression
        self.compile_expression()

        # neg the expression as instructed in the lectures
        self.vmwriter.write_arithmetic("NOT")

        # ')'
        self.tokenizer.advance()

        # '{'
        self.tokenizer.advance()

        # if-goto == true then end while as stated in the lectures
        self.vmwriter.write_if("WHILE_END." + str(cur_id))

        # statements
        self.compile_statements()

        # '}'
        self.tokenizer.advance()

        # loop the while
        self.vmwriter.write_goto("WHILE_START." + str(cur_id))

        self.vmwriter.write_label("WHILE_END." + str(cur_id))

    def compile_return(self) -> None:  ############ DONE
        """Compiles a return statement."""

        # "return"
        #print("return: ", self.tokenizer.token())
        self.tokenizer.advance()

        if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ";"):
            self.vmwriter.write_push("CONSTANT", 0)

        else:
            self.compile_expression()

        self.vmwriter.write_return()

        self.tokenizer.advance()

    def compile_if(self) -> None:  ############ DONE
        """Compiles a if statement, possibly with a trailing else clause."""

        self.subroutine_id += 1
        cur_id = self.subroutine_id

        while self.tokenizer.symbol() != "(":
            #print("if")
            self.tokenizer.advance()

        # '('
        #print("(: ", self.tokenizer.token())
        self.tokenizer.advance()

        # expression
        #print("expression in if ", self.tokenizer.token())
        self.compile_expression()
        self.vmwriter.write_arithmetic("NOT")

        # ')'
        #print("): ", self.tokenizer.token())
        self.tokenizer.advance()

        # '{'
        #print("{: ", self.tokenizer.token())
        self.tokenizer.advance()

        # writing if
        self.vmwriter.write_if("IF_START." + str(cur_id))

        # statements
        self.compile_statements()

        # '}'
        #print("}: ", self.tokenizer.token())
        self.tokenizer.advance()

        # end of if meaning the expression was true so jump to end of whole if and skip the 'else'
        self.vmwriter.write_goto("IF_END." + str(cur_id))

        self.vmwriter.write_label("IF_START." + str(cur_id))

        if (self.tokenizer.token_type() == "KEYWORD"):
            if (self.tokenizer.keyword() == "ELSE"):
                # 'else'
                #print("else: ", self.tokenizer.token())
                self.tokenizer.advance()

                # '{'
                #print("{: ", self.tokenizer.token())
                self.tokenizer.advance()

                # statements
                self.compile_statements()

                # '}'
                #print("}: ", self.tokenizer.token())
                self.tokenizer.advance()

        self.vmwriter.write_label("IF_END." + str(cur_id))

    def compile_expression(self) -> None:  ############ DONE
        """Compiles an expression."""
        self.compile_term()
        operator_symbol = ""

        # check if next token is an operator symbol and if so compile the next term
        while (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() in ['+', '-', '*', '/', '&', '|',
                                                                                       '<', '>', '=']):
            #print("expression")
            if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() in ['+', '-', '*', '/', '&', '|',
                                                                                        '<', '>', '=']):
                operator_symbol = self.tokenizer.symbol()
                self.tokenizer.advance()
            self.compile_term()
            if operator_symbol in ["*", "/"]:
                self.vmwriter.write_call(self.bi_operators_to_word[operator_symbol], 2)
                #print(operator_symbol)
            else:
                self.vmwriter.write_arithmetic(self.bi_operators_to_word[operator_symbol])
                #print(operator_symbol)

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

        prev_token_type = self.tokenizer.token_type()
        prev_token_symbol = self.tokenizer.symbol()

        if (prev_token_type == "SYMBOL" and prev_token_symbol == "("):
            #print("symbol in term before compiling another expression: ", self.tokenizer.token())
            self.tokenizer.advance()
            self.compile_expression()
            self.tokenizer.advance()
            return

        if (self.tokenizer.token_type() == "INT_CONST"):
            self.vmwriter.write_push("CONSTANT", self.tokenizer.int_val())
            #print("INT_CONST: ", self.tokenizer.token())
            self.tokenizer.advance()

        elif self.tokenizer.token_type() == "STRING_CONST":

            self.vmwriter.write_push("CONSTANT", len(self.tokenizer.string_val()))
            self.vmwriter.write_call("String.new", 1)
            #print("STRING_CONST: ", self.tokenizer.token())
            for c in self.tokenizer.string_val():
                self.vmwriter.write_push("CONSTANT", ord(c))
                self.vmwriter.write_call("String.appendChar", 2)

            self.tokenizer.advance()

        # can be only one of - ['true', 'false', 'null', 'this']
        elif (self.tokenizer.token_type() == "KEYWORD"):
            #print("keyword in term: ", self.tokenizer.token())
            if self.tokenizer.keyword() == "THIS":
                self.vmwriter.write_push("POINTER", 0)

            elif self.tokenizer.keyword() in ["TRUE", "FALSE", "NULL"]:
                if self.tokenizer.keyword() == "TRUE":
                    self.vmwriter.write_push("CONSTANT", 1)
                    self.vmwriter.write_arithmetic("NEG")
                else:
                    self.vmwriter.write_push("CONSTANT", 0)

            self.tokenizer.advance()

        elif self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() in ['-', '~', '^', '#']:

            op_symbol = self.tokenizer.symbol()
            #print(op_symbol)
            self.tokenizer.advance()
            #print("item after:" + str(op_symbol) + " in term making: ", self.tokenizer.token())
            self.compile_term()
            self.vmwriter.write_arithmetic(self.un_operators_to_word[op_symbol])

        elif self.tokenizer.token_type() == "IDENTIFIER":
            self.check_identifier()

    def compile_expression_list(self) -> int:  ############ DONE
        """Compiles a (possibly empty) comma-separated list of expressions."""
        amount_of_args_in_expression_list = 0

        #print("first item before while in expression_list: ", self.tokenizer.token())

        while (self.tokenizer.symbol() != ")"):

            if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == ","):
                #print("separator ',' in expression list: ", self.tokenizer.token())
                self.tokenizer.advance()
            else:
                # #print("next item in expression list: ", self.tokenizer.token())
                #print("next item before while in expression_list: ", self.tokenizer.token())
                self.compile_expression()
                amount_of_args_in_expression_list += 1
                # self.tokenizer.advance()
        return amount_of_args_in_expression_list

    def check_identifier(self):
        # print("identifier name: ", self.tokenizer.token())

        name = self.tokenizer.identifier()
        # print(name)
        # print("CHECKING IF LENGTH IS IN SYMBOL TABLEEEEEEEEEEEE: ", self.symbol_table.type_of(name) != None)
        self.tokenizer.advance()
        args = 0
        # print("next token after identifier advanced in term: ", self.tokenizer.token())

        if (self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() in ["[", ".", "("]):
            if (self.tokenizer.symbol() == "["):
                # print("AAAAA")

                # '['
                # print("[ :", self.tokenizer.token())
                self.tokenizer.advance()
                # print("token before compiling expression: ", self.tokenizer.token())
                self.compile_expression()

                # ']'
                # print("]: ", self.tokenizer.token())
                self.tokenizer.advance()

                kind = self.symbol_table.kind_of(name)
                index = self.symbol_table.index_of(name)

                if kind == "FIELD":
                    self.vmwriter.write_push("THIS", index)
                elif kind == "STATIC":
                    self.vmwriter.write_push("STATIC", index)
                elif kind == "ARG":
                    self.vmwriter.write_push("ARGUMENT", index)
                elif kind == "VAR":
                    self.vmwriter.write_push("LOCAL", index)

                # base arr address + deviation
                self.vmwriter.write_arithmetic("ADD")

                # look at the wanted arr item which moves 'THAT' to have its address
                self.vmwriter.write_pop("pointer", 1)

                self.vmwriter.write_push("that", 0)

            elif (self.tokenizer.symbol() == "."):
                # '.'
                # print(". : ", self.tokenizer.token())
                self.tokenizer.advance()
                # print("func_name: ", name + "." + self.tokenizer.token())
                func_name = name + "." + self.tokenizer.identifier()
                self.tokenizer.advance()

                # checking to see if the first identifier exists in the symbol table, if so then that means we called a
                # method through it, so by the convention we learnt in the lectures we must save that object and then
                # call the method through the CLASS name, that's why we change the func_name to include the class name
                # instead of the prior name which is the objects's name. otherwise then that means we did not go into
                # the if statement which means we called a method through a Class name and all is good.
                if self.symbol_table.type_of(name) != None:
                    args += 1
                    type = self.symbol_table.type_of(name)
                    kind = self.symbol_table.kind_of(name)
                    index = self.symbol_table.index_of(name)
                    # print("details of identifier in term with '.': ",type, kind, index)

                    if kind == "FIELD":
                        self.vmwriter.write_push("THIS", index)
                    elif kind == "STATIC":
                        self.vmwriter.write_push("STATIC", index)
                    elif kind == "ARG":
                        self.vmwriter.write_push("ARGUMENT", index)
                    elif kind == "VAR":
                        self.vmwriter.write_push("LOCAL", index)

                    func_name = type + "." + func_name.split(".")[1]

                # "("
                # print("(", self.tokenizer.token())
                self.tokenizer.advance()

                args += self.compile_expression_list()
                # print(args)

                # ")"
                # print(") ", self.tokenizer.token())
                self.tokenizer.advance()

                self.vmwriter.write_call(func_name, args)

            elif (self.tokenizer.symbol() == "("):

                func_name = ""
                # print("name of method in term with just ( : ", name)
                if self.symbol_table.type_of(name) != None:
                    args += 1
                    type = self.symbol_table.type_of(name)
                    kind = self.symbol_table.kind_of(name)
                    index = self.symbol_table.index_of(name)
                    # print("details of identifier in term with '.': ", type, kind, index)

                    if kind == "FIELD":
                        self.vmwriter.write_push("THIS", index)
                    elif kind == "STATIC":
                        self.vmwriter.write_push("STATIC", index)
                    elif kind == "ARG":
                        self.vmwriter.write_push("ARGUMENT", index)
                    elif kind == "VAR":
                        self.vmwriter.write_push("LOCAL", index)

                    func_name = type + "." + func_name.split(".")[1]

                # "("
                # print("( ", self.tokenizer.token())
                self.tokenizer.advance()

                args += self.compile_expression_list()

                # ")"
                # print(") ", self.tokenizer.token())
                self.tokenizer.advance()

                if '.' in func_name:
                    # print("writing call to function with name: ", func_name, "and args: ", args)
                    self.vmwriter.write_call(func_name, args)

                else:
                    self.vmwriter.write_push("THIS", 0)
                    func_name = self.class_tag + "." + name
                    self.vmwriter.write_call(func_name, args)

            # elif (self.tokenizer.symbol() in ['-', '~', '^', '#']):
            #         op_symbol = self.tokenizer.symbol()
            #         #print(op_symbol)
            #         self.tokenizer.advance()
            #         #print("item after:" + str(op_symbol) + " in term making: ", self.tokenizer.token())
            #         self.compile_term()
            #         self.vmwriter.write_arithmetic(self.un_operators_to_word[op_symbol])

        elif self.symbol_table.type_of(name) != None:
            # print("555555555555")
            kind = self.symbol_table.kind_of(name)
            index = self.symbol_table.index_of(name)
            # print("kind and index of identifier: ", kind, index)
            if kind == "FIELD":
                self.vmwriter.write_push("THIS", index)
            elif kind == "STATIC":
                self.vmwriter.write_push("STATIC", index)
            elif kind == "ARG":
                self.vmwriter.write_push("ARGUMENT", index)
            elif kind == "VAR":
                self.vmwriter.write_push("LOCAL", index)
