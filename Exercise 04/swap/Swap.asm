// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

// Put your code here.

// making a variable to point to the current index we're checking
@R14
D=M
@cur_index
M=D // cur_index = R14

// setting min_val and max_val addresses to start of the array
@cur_index
A=M
D=A
@min_val_address
M=D
@max_val_address
M=D


(LOOP)
	// check if reached end of array
	@cur_index
	D=M
	@R14
	D=D-M
	@R15
	D=D-M
	@SWAP
	D;JGE

	@cur_index
	M=M+1
	A=M
	D=M // D has current value of next item in array

	// check if reached end of array
	@cur_index
	D=M
	@R14
	D=D-M
	@R15
	D=D-M
	@SWAP
	D;JGE

	@cur_index
	A=M
	D=M

	// check if cur item is bigger than max, D has address of current item in the array
	@max_val_address
	A=M
	D=D-M //arr[i] - max
	// if D>0 that means cur item is > max, else cur item is <= max and no jump needed
	@CHANGE_MAX_TO_CUR
	D;JGT

	@cur_index
	A=M
	D=M

	// check if cur item is smaller than min, D has address of current item in the array
	@min_val_address
	A=M
	D=D-M //arr[i] - min
	// if D<0 that means cur item is < min, else cur item is >= min and no jump needed
	@CHANGE_MIN_TO_CUR
	D;JLT

	@CONTINUE
	0;JMP

	(CHANGE_MAX_TO_CUR)
		@cur_index
		A=M
		D=A
		@max_val_address
		M=D
		@CONTINUE
		0;JMP

	(CHANGE_MIN_TO_CUR)
		@cur_index
		A=M
		D=A
		@min_val_address
		M=D

	(CONTINUE)
	// check if reached end of array
	@cur_index
	D=M
	@R14
	D=D-M
	@R15
	D=D-M
	@SWAP
	D;JGE


	@LOOP
	0;JMP

(SWAP)
	@min_val_address
	A=M
	D=M
	@min_val_real
	M=D
	@max_val_address
	A=M
	D=M
	@max_val_real
	M=D
	D=M //D has the max number VALUE

	@min_val_address
	A=M
	M=D //now min val address memory has the max number

	@min_val_real
	D=M //D has the min number value

	@max_val_address
	A=M
	M=D //now max val address memory has the min number

(END)
  @END
  0;JMP
	














