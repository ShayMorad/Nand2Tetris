"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def clean_lines(self):
        cleaned_lines = []
        for line in self.input_lines:
            # Remove leading and trailing whitespaces
            cleaned_line = line.strip()

            # Remove comments starting with '//'
            if '//' in cleaned_line:
                cleaned_line = cleaned_line.split('//')[0].strip()

            # Remove extra whitespaces within the command
            cleaned_line = ' '.join(cleaned_line.split())
            if ' ' in cleaned_line:
                cleaned_line = cleaned_line.replace(' ', '')
            # Add the cleaned line to the list if it's not empty
            if cleaned_line:
                cleaned_lines.append(cleaned_line)

        # Update self.input_lines with the cleaned lines
        self.input_lines = cleaned_lines

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        self.input_lines = input_file.read().splitlines()
        self.clean_lines()
        self.current_line = 0
        self.current_command = None

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        if self.current_line < len(self.input_lines):
            return True
        return False

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        if self.has_more_commands():
            self.current_command = self.input_lines[self.current_line]
            self.current_line += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if self.current_command[0] == '@':
            return 'A_COMMAND'
        elif self.current_command[0] == '(':
            return "L_COMMAND"
        return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        if self.command_type() == 'A_COMMAND':
            return self.current_command.replace('@','')
        elif self.command_type() == "L_COMMAND":
            return self.current_command.replace('(','').replace(')','')

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if "=" in self.current_command and self.command_type() == "C_COMMAND":
            return self.current_command.split('=')[0].strip()


    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if '=' in self.current_command:
            cur = self.current_command.split('=')
            return cur[1].split(';')[0].strip()
        return self.current_command.split(';')[0].strip()

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if ';' in self.current_command:
            return self.current_command.split(';')[1].strip()



