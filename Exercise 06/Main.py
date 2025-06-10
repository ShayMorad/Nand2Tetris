"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    table = SymbolTable()
    parser = Parser(input_file)
    rom = 0
    while parser.has_more_commands():
        parser.advance()
        if parser.command_type() == 'L_COMMAND':
            table.add_entry(parser.symbol(), rom)
        else:
            rom += 1

    parser.current_line = 0
    parser.current_command = None
    ram = 16

    while parser.has_more_commands():
        parser.advance()

        if parser.command_type() == 'A_COMMAND':
            if parser.symbol().isnumeric():
                continue
            elif not table.contains(parser.symbol()):
                table.add_entry(parser.symbol(), ram)
                ram += 1

    parser.current_line = 0
    parser.current_command = None
    code = Code()
    while parser.has_more_commands():
        parser.advance()

        if parser.command_type() == 'A_COMMAND':
            if parser.symbol().isnumeric():
                output_file.write(bin(int(parser.symbol()))[2:].zfill(16) + "\n")
            else:
                output_file.write(bin(table.get_address(parser.symbol()))[2:].zfill(16) + "\n")
        elif parser.command_type() == 'C_COMMAND':
            temp = '111'
            if '<<' in parser.comp() or '>>' in parser.comp():
                temp = '101'
            temp += code.comp(parser.comp())
            temp += code.dest(parser.dest())
            temp += code.jump(parser.jump())
            output_file.write(temp + '\n')
        elif parser.command_type() == 'L_COMMAND':
            continue


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
