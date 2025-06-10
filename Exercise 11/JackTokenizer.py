"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the lines end.

    - 'xxx': quotes are used for tokens that appear verbatim ('terminals').
    - xxx: regular typeface is used for names of language constructs 
           ('non-terminals').
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        self.input_lines = input_stream.read().splitlines()
        self.input_lines = self.remove_comments()
        self.input_lines = [item for item in self.input_lines if item != '""']
        self.keywords = ['class', 'constructor', 'function', 'method', 'field',
                         'static', 'var', 'int', 'char', 'boolean', 'void', 'true',
                         'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
        self.symbols = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
                        '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#']
        self.tokens = []

        self.tokens_type = dict()
        self.create_tokens_arr()
        self.cur_token = 0

    def remove_comments(self):
        cleaned_lines = []
        in_string = False
        in_block_comment = False

        for line in self.input_lines:
            cleaned_line = ''
            index = 0
            while index < len(line):
                if line[index] == '"':
                    # Toggle the in_string flag when encountering a double quote
                    in_string = not in_string
                    cleaned_line += line[index]
                    index += 1
                    continue

                if not in_string:
                    if index + 1 < len(line) and line[index:index + 2] == '//':
                        # If not within a string, remove // style comments
                        break

                    if index + 1 < len(line) and line[index:index + 2] == '/*':
                        # If not within a string, mark the beginning of a block comment
                        in_block_comment = True
                        index += 2
                        continue

                    if index + 1 < len(line) and line[index:index + 2] == '*/':
                        # If not within a string, mark the end of a block comment
                        in_block_comment = False
                        index += 2
                        continue

                # If not in a block comment, add the character to the cleaned line
                if not in_block_comment:
                    cleaned_line += line[index]
                index += 1

            # Add the cleaned line to the list

            if (line.strip() != ""):
                cleaned_lines.append(cleaned_line.strip())

        return cleaned_lines

    def create_tokens_arr(self):

        for line in self.input_lines:
            token = ""

            for i in range(len(line)):
                char = line[i]
                if (token == "" and (char == " " or char == "\n" or char == "\r" or char == "\t")):
                    continue
                token += char

                if token in self.symbols:
                    token = ''.join(token.split())
                    self.tokens.append(token)
                    self.tokens_type[token] = "SYMBOL"
                    token = ""
                    continue

                elif len(token) >= 2 and token[0] == '"' and token[-1] == '"':
                    self.tokens.append(token)
                    self.tokens_type[token] = "STRING_CONST"
                    token = ""
                    continue

                elif token.isdigit() and (
                        (i == len(line) - 1) or (i < (len(line) - 1) and (not line[i + 1].isdigit()))):
                    token = ''.join(token.split())
                    self.tokens.append(token)
                    self.tokens_type[token] = "INT_CONST"
                    token = ""
                    continue

                elif token in self.keywords and ((i == len(line) - 1) or
                                                 (i < (len(line) - 1) and (
                                                         (line[i + 1] == " ") or (line[i + 1] == "\t") or
                                                         (line[i + 1] == "\n") or (line[i + 1] == "\r") or (
                                                                 line[i + 1] in self.symbols)))):
                    token = ''.join(token.split())
                    self.tokens.append(token)
                    self.tokens_type[token] = "KEYWORD"

                    token = ""
                    continue

                elif (i == len(line) - 1) or (
                        i < (len(line) - 1) and ((line[i + 1] == " ") or (line[i + 1] in self.symbols))):
                    if token != " " and token[0] != '"':
                        token = ''.join(token.split())
                        self.tokens.append(token)
                        self.tokens_type[token] = "IDENTIFIER"
                        token = ""
                        continue

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        if (self.cur_token < len(self.tokens) - 1):
            return True
        return False

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        if (self.has_more_tokens()):
            self.cur_token += 1

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        current_token = self.tokens[self.cur_token]
        return self.tokens_type[current_token]

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        current_token = self.tokens[self.cur_token]
        return current_token.upper()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        current_token = self.tokens[self.cur_token]
        return current_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        current_token = self.tokens[self.cur_token]
        return current_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        current_token = self.tokens[self.cur_token]
        return int(current_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        current_token = self.tokens[self.cur_token][1:-1]
        return current_token

    def token(self):
        return str(self.tokens[self.cur_token])

