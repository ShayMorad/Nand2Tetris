"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""
    command_count = 0
    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.output_stream = output_stream
        self.file_name = ""


    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        #if self.file_name != filename:
        self.file_name = filename
        #    self.file_count += 1

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """

        CodeWriter.command_count+=1

        if command == "add":
            self.output_stream.write("@SP\n"
                                     "A=M-1\n"
                                     "D=M\n"
                                     "A=A-1\n"
                                     "M=D+M\n"
                                     "@SP\n"
                                     "M=M-1\n")
        elif command == "sub":
            self.output_stream.write("@SP\n"
                                     "A=M-1\n"
                                     "D=M\n"
                                     "A=A-1\n"
                                     "M=M-D\n"
                                     "@SP\n"
                                     "M=M-1\n")
        elif command == "neg":
            self.output_stream.write("@SP\n"
                                     "A=M-1\n"
                                     "M=-M\n")
        elif command == "eq":
            self.output_stream.write(
                 "@SP\n"
                 "A=M-1\n"
                 "D=M\n"  # D = Y
                 "@Y_NEGATIVE" + str(CodeWriter.command_count)+"\n"
                 "D;JLT\n"  # jump only if Y is negative
                 "@SP\n"    # Y is positive
                 "A=M-1\n"
                 "A=A-1\n"  # A has x address, M=X
                 "D=M\n"
                 "@CAN_SUB" + str(CodeWriter.command_count)+"\n"  # Y is positive
                 "D;JGE\n"    # jump to CAN_SUB only if X is >= 0 and Y is >=0
                 "@FALSE" + str(CodeWriter.command_count)+"\n"
                 "0;JMP\n"
                 "(Y_NEGATIVE" + str(CodeWriter.command_count)+")\n"
                 "@SP\n"
                 "A=M-1\n"
                 "A=A-1\n"  # A has X address, M=X
                 "D=M\n"
                 "@CAN_SUB" + str(CodeWriter.command_count)+"\n"
                 "D;JLT\n"  # jump to CAN_SUB only if x is negative and y is negative
                 "(FALSE" + str(CodeWriter.command_count)+")\n"
                 "@SP\n"         # if no jump then X is positive and Y is negative, therefore eq == false
                 "A=M-1\n"
                 "A=A-1\n"
                 "M=0\n"
                 "@END" + str(CodeWriter.command_count)+"\n"
                 "0;JMP\n"
                 "(CAN_SUB" + str(CodeWriter.command_count)+")\n"
                 "@SP\n"
                 "A=M-1\n"
                 "D=M\n"
                 "A=A-1\n"
                 "M=M-D\n"   # M = X - Y
                 "D=M\n"
                 "@FALSE" + str(CodeWriter.command_count)+"\n"                           
                 "D;JNE\n"
                 "@SP\n"
                 "A=M-1\n"
                 "A=A-1\n"
                 "M=-1\n"
                 "(END" + str(CodeWriter.command_count)+")\n"
                 "@SP\n"
                 "M=M-1\n")

        elif command == "gt":
            self.output_stream.write(
                 "@SP\n"
                 "A=M-1\n"
                 "D=M\n"  # D = Y
                 "@Y_NEGATIVE" + str(CodeWriter.command_count)+"\n"
                 "D;JLT\n"  # jump only if Y is negative
                 "@SP\n"    # Y is positive
                 "A=M-1\n"
                 "A=A-1\n"  # A has x address, M=X
                 "D=M\n"
                 "@CAN_SUB" + str(CodeWriter.command_count)+"\n"  # Y is positive
                 "D;JGE\n"    # jump to CAN_SUB only if X is positive and Y is positive
                 "@FALSE" + str(CodeWriter.command_count)+"\n"
                 "0;JMP\n"
                 "(Y_NEGATIVE" + str(CodeWriter.command_count)+")\n"
                 "@SP\n"
                 "A=M-1\n"
                 "A=A-1\n"  # A has X address, M=X
                 "D=M\n"
                 "@CAN_SUB" + str(CodeWriter.command_count)+"\n"
                 "D;JLT\n"  # jump to CAN_SUB only if x is negative and y is negative
                 "@SP\n"
                 "A=M-1\n"
                 "A=A-1\n"
                 "M=-1\n"
                 "@END" + str(CodeWriter.command_count)+"\n"
                 "0;JMP\n"
                 "(FALSE" + str(CodeWriter.command_count)+")\n"
                 "@SP\n"         # if no jump then X is positive and Y is negative, therefore eq == false
                 "A=M-1\n"
                 "A=A-1\n"
                 "M=0\n"
                 "@END" + str(CodeWriter.command_count)+"\n"
                 "0;JMP\n"
                 "(CAN_SUB" + str(CodeWriter.command_count)+")\n"
                 "@SP\n"
                 "A=M-1\n"
                 "D=M\n"
                 "A=A-1\n"
                 "M=M-D\n"   # M = X - Y
                 "D=M\n"
                 "@FALSE" + str(CodeWriter.command_count)+"\n"                           
                 "D;JLE\n"
                 "@SP\n"
                 "A=M-1\n"
                 "A=A-1\n"
                 "M=-1\n"
                 "(END" + str(CodeWriter.command_count)+")\n"
                 "@SP\n"
                 "M=M-1\n")
        elif command == "lt":
            self.output_stream.write(
                 "@SP\n"
                 "A=M-1\n"
                 "D=M\n"  # D = Y
                 "@Y_NEGATIVE" + str(CodeWriter.command_count)+"\n"
                 "D;JLT\n"  # jump only if Y is negative
                 "@SP\n"    # Y is positive
                 "A=M-1\n"
                 "A=A-1\n"  # A has x address, M=X
                 "D=M\n"
                 "@CAN_SUB" + str(CodeWriter.command_count)+"\n"  # Y is positive
                 "D;JGE\n"    # jump to CAN_SUB only if X is positive and Y is positive
                 "@SP\n"
                 "A=M-1\n"
                 "A=A-1\n"
                 "M=-1\n"
                 "@END" + str(CodeWriter.command_count)+"\n"
                 "0;JMP\n"
                 "(Y_NEGATIVE" + str(CodeWriter.command_count)+")\n"
                 "@SP\n"
                 "A=M-1\n"
                 "A=A-1\n"  # A has X address, M=X
                 "D=M\n"
                 "@CAN_SUB" + str(CodeWriter.command_count)+"\n"
                 "D;JLT\n"  # jump to CAN_SUB only if x is negative and y is negative
                 "(FALSE" + str(CodeWriter.command_count)+")\n"
                 "@SP\n"         # if no jump then X is positive and Y is negative, therefore eq == false
                 "A=M-1\n"
                 "A=A-1\n"
                 "M=0\n"
                 "@END" + str(CodeWriter.command_count)+"\n"
                 "0;JMP\n"
                 "(CAN_SUB" + str(CodeWriter.command_count)+")\n"
                 "@SP\n"
                 "A=M-1\n"
                 "D=M\n"
                 "A=A-1\n"
                 "M=M-D\n"   # M = X - Y
                 "D=M\n"
                 "@FALSE" + str(CodeWriter.command_count)+"\n"                           
                 "D;JGE\n"
                 "@SP\n"
                 "A=M-1\n"
                 "A=A-1\n"
                 "M=-1\n"
                 "(END" + str(CodeWriter.command_count)+")\n"
                 "@SP\n"
                 "M=M-1\n")
        elif command == "and":
            self.output_stream.write("@SP\n"
                                     "A=M-1\n"
                                     "D=M\n"
                                     "A=A-1\n"
                                     "M=D&M\n"
                                     "@SP\n"
                                     "M=M-1\n")
        elif command == "or":
            self.output_stream.write("@SP\n"
                                     "A=M-1\n"
                                     "D=M\n"
                                     "A=A-1\n"
                                     "M=D|M\n"
                                     "@SP\n"
                                     "M=M-1\n")
        elif command == "not":
            self.output_stream.write("@SP\n"
                                     "A=M-1\n"
                                     "M=!M\n")

        elif command == "shiftleft":
            self.output_stream.write("@SP\n"
                                     "A=M-1\n"
                                     "D=M<<\n"
                                     "M=D\n")
        elif command == "shiftright":
            self.output_stream.write("@SP\n"
                                     "A=M-1\n"
                                     "D=M>>\n"
                                     "M=D\n")


    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.

        if command == "C_PUSH":
            if segment == "local":
                self.output_stream.write("@LCL\n"
                                         "D=M\n"
                                         "@" + str(index) + "\n"
                                                            "D=D+A\n"
                                                            "A=D\n"  # A = LCL+INDEX ADDRESS
                                                            "D=M\n"  # D = LCL+INDEX MEMORY
                                                            "@SP\n"
                                                            "A=M\n"
                                                            "M=D\n"
                                                            "@SP\n"
                                                            "M=M+1\n")
            elif segment == "argument":
                self.output_stream.write("@ARG\n"
                                         "D=M\n"
                                         "@" + str(index) + "\n"
                                                            "D=D+A\n"
                                                            "A=D\n"  # A = ARG+INDEX
                                                            "D=M\n"
                                                            "@SP\n"
                                                            "A=M\n"
                                                            "M=D\n"
                                                            "@SP\n"
                                                            "M=M+1\n")
            elif segment == "this":
                self.output_stream.write("@THIS\n"
                                         "D=M\n"
                                         "@" + str(index) + "\n"
                                                            "D=D+A\n"
                                                            "A=D\n"  # A = THIS+INDEX
                                                            "D=M\n"
                                                            "@SP\n"
                                                            "A=M\n"
                                                            "M=D\n"
                                                            "@SP\n"
                                                            "M=M+1\n")
            elif segment == "that":
                self.output_stream.write("@THAT\n"
                                         "D=M\n"
                                         "@" + str(index) + "\n"
                                                            "D=D+A\n"
                                                            "A=D\n"  # A = THAT+INDEX
                                                            "D=M\n"
                                                            "@SP\n"
                                                            "A=M\n"
                                                            "M=D\n"
                                                            "@SP\n"
                                                            "M=M+1\n")

            elif segment == "constant":
                self.output_stream.write("@" + str(index) + "\n"
                                                            "D=A\n"
                                                            "@SP\n"
                                                            "A=M\n"
                                                            "M=D\n"
                                                            "@SP\n"
                                                            "M=M+1\n")
            elif segment == "static":
                self.output_stream.write("@" + self.file_name + "." + str(index) + "\n"
                                                                                   "D=M\n"
                                                                                   "@SP\n"
                                                                                   "A=M\n"
                                                                                    "M=D\n"
                                                                                   "@SP\n"
                                                                                   "M=M+1\n")

            elif segment == "pointer":
                pointer_index = 3 + index
                self.output_stream.write("@" + str(pointer_index) + "\n"
                                                                    "D=M\n"
                                                                    "@SP\n"
                                                                    "A=M\n"
                                                                    "M=D\n"
                                                                    "@SP\n"
                                                                    "M=M+1\n")

            elif segment == "temp":
                temp_index = 5 + index
                self.output_stream.write("@" + str(temp_index) + "\n"
                                                                 "D=M\n"
                                                                 "@SP\n"
                                                                 "A=M\n"
                                                                 "M=D\n"
                                                                 "@SP\n"
                                                                 "M=M+1\n")

        elif command == "C_POP":
            if segment == "local":
                self.output_stream.write("@SP\n"
                                         "A=M-1\n"
                                         "D=M\n"  # D HAS POP VALUE
                                         "@R13\n"
                                         "M=D\n"  # R13 HAS POP VALUE
                                         "@LCL\n"
                                         "D=M\n"
                                         "@" + str(index) + "\n"
                                                            "D=D+A\n"  # D HAS LCL+INDEX ADDRESS
                                                            "@R14\n"
                                                            "M=D\n"  # R14 HAS LCL_INDEX ADDRESS
                                                            "@R13\n"
                                                            "D=M\n"  # D HAS POP VALUE
                                                            "@R14\n"
                                                            "A=M\n"  # A HAS LCL+INDEX
                                                            "M=D\n"
                                                            "@SP\n"
                                                            "M=M-1\n")
            elif segment == "argument":
                self.output_stream.write("@SP\n"
                                         "A=M-1\n"
                                         "D=M\n"  # D HAS POP VALUE
                                         "@R13\n"
                                         "M=D\n"  # R13 HAS POP VALUE
                                         "@ARG\n"
                                         "D=M\n"
                                         "@" + str(index) + "\n"
                                                            "D=D+A\n"  # D HAS ARG+INDEX ADDRESS
                                                            "@R14\n"
                                                            "M=D\n"  # R14 HAS ARG+INDEX ADDRESS
                                                            "@R13\n"
                                                            "D=M\n"  # D HAS POP VALUE
                                                            "@R14\n"
                                                            "A=M\n"  # A HAS ARG+INDEX
                                                            "M=D\n"
                                                            "@SP\n"
                                                            "M=M-1\n")

            elif segment == "this":
                self.output_stream.write("@SP\n"
                                         "A=M-1\n"
                                         "D=M\n"  # D HAS POP VALUE
                                         "@R13\n"
                                         "M=D\n"  # R13 HAS POP VALUE
                                         "@THIS\n"
                                         "D=M\n"
                                         "@" + str(index) + "\n"
                                                            "D=D+A\n"  # D HAS THIS+INDEX ADDRESS
                                                            "@R14\n"
                                                            "M=D\n"  # R14 HAS THIS+INDEX ADDRESS
                                                            "@R13\n"
                                                            "D=M\n"  # D HAS POP VALUE
                                                            "@R14\n"
                                                            "A=M\n"  # A HAS THIS+INDEX
                                                            "M=D\n"
                                                            "@SP\n"
                                                            "M=M-1\n")

            elif segment == "that":
                self.output_stream.write("@SP\n"
                                         "A=M-1\n"
                                         "D=M\n"  # D HAS POP VALUE
                                         "@R13\n"
                                         "M=D\n"  # R13 HAS POP VALUE
                                         "@THAT\n"
                                         "D=M\n"
                                         "@" + str(index) + "\n"
                                                            "D=D+A\n"  # D HAS THAT+INDEX ADDRESS
                                                            "@R14\n"
                                                            "M=D\n"  # R14 HAS THAT+INDEX ADDRESS
                                                            "@R13\n"
                                                            "D=M\n"  # D HAS POP VALUE
                                                            "@R14\n"
                                                            "A=M\n"  # A HAS THAT+INDEX
                                                            "M=D\n"
                                                            "@SP\n"
                                                            "M=M-1\n")
            elif segment == "static":
                self.output_stream.write("@SP\n"
                                         "A=M-1\n"
                                         "D=M\n"  # D HAS POP VALUE
                                         "@" + self.file_name + "." + str(index) + "\n"
                                                                                   "M=D\n"  # INSERT D TO M
                                                                                   "@SP\n"
                                                                                   "M=M-1\n")

            elif segment == "pointer":
                pointer_index = 3 + index
                self.output_stream.write("@SP\n"
                                         "A=M-1\n"
                                         "D=M\n"  # D HAS POP VALUE
                                         "@" + str(pointer_index) + "\n"
                                                                    "M=D\n"  # INSERT D TO M
                                                                    "@SP\n"
                                                                    "M=M-1\n")

            elif segment == "temp":
                temp_index = 5 + index
                self.output_stream.write("@SP\n"
                                         "A=M-1\n"
                                         "D=M\n"  # D HAS POP VALUE
                                         "@" + str(temp_index) + "\n"
                                                                 "M=D\n"  # INSERT D TO M
                                                                 "@SP\n"
                                                                 "M=M-1\n")

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        pass

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        pass

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        pass
