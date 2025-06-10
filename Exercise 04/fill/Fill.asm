// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// This program illustrates low-level handling of the screen and keyboard
// devices, as follows.
//
// The program runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.
// 
// Assumptions:
// Your program may blacken and clear the screen's pixels in any spatial/visual
// Order, as long as pressing a key continuously for long enough results in a
// fully blackened screen, and not pressing any key for long enough results in a
// fully cleared screen.
//
// Test Scripts:
// For completeness of testing, test the Fill program both interactively and
// automatically.
// 
// The supplied FillAutomatic.tst script, along with the supplied compare file
// FillAutomatic.cmp, are designed to test the Fill program automatically, as 
// described by the test script documentation.
//
// The supplied Fill.tst script, which comes with no compare file, is designed
// to do two things:
// - Load the Fill.hack program
// - Remind you to select 'no animation', and then test the program
//   interactively by pressing and releasing some keyboard keys

// Put your code here.

(LOOP)
  // setting index to 8191 because there are 8191 registers of the screen
  @8191
  D=A
  @index
  M=D

  // checking keyboard
  @KBD
  D=M
  
  // If any button was pressed, color screen BLACK
  @BLACK
  D;JNE

  // else we want to color screen WHITE
  (WHITE)
    @SCREEN
    D=A

    @index
    D=D+M
    A=D
    M=0

    @index
    M=M-1
    
    //  if index is greater equal 0 loop to WHITE because there are more pixels to color white
    D=M
    @WHITE
    D;JGE
    
    // else, goto LOOP
    @LOOP
    0;JMP

  (BLACK)
    @SCREEN
    D=A
    @index
    D=D+M
    A=D
    M=-1

    @index
    M=M-1
    
    // if index is greater equal to 0 loop to BLACK because there are more pixels to color white
    D=M
    @BLACK
    D;JGE
    
    // else loop
    @LOOP
    0;JMP