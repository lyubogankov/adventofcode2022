# Advent of Code 2022
[adventofcode.com/2022/](https://adventofcode.com/2022/)

I read about Advent of Code earlier this year and was excited to participate once December rolled around!

The [About / FAQ](https://adventofcode.com/2022/about) page summarizes it best:

> Advent of Code is an Advent calendar of small programming puzzles... that can be solved in any programming language you like.

> The difficulty and subject matter varies throughout each event. Very generally, the puzzles get more difficult over time[.]

Each puzzle consists of two related parts, but the description for the second part is only available once a correct solution to the first part has been found and entered into the puzzle page.

The puzzle inputs are text files.  A worked example given in the problem description, and a larger or more complicated input is provided for the actual puzzle. My solution should work on both!  The same example/complicated inputs are used for both parts of each day's puzzle.

## My goals

- **Have fun!**  I used Python for my solutions because I am already comfortable with its syntax and features - I could focus on how to structure my approach to the problem (instead of also worrying about learning a new language on top of that!).

- **Write extensible solutions**  After completing the first several puzzles, I began noticing that each puzzle's two parts were somehow related.
    - My goal from Day 05 onwards was to implement one solution that can answer both parts of the puzzle with as much shared code as possible.  This usually involves refactoring once I finish part one and read over the second part's puzzle description.
    - From Day 10 onwards, I began trying to predict which elements could change from parts one -> two.  I write a list of what might change and try to write my code such that these changes won't be painful to make.  While I haven't correctly guessed the change yet, this has been a useful thought exercise and has resulted in more modular code!

- **Practice writing unit tests**  I've been strongly advised by two different mentors to write unit tests for my code.  As the puzzles became more complicated, I found myself spending a lot of time trying to match up my solution's console printout to the problem description's worked example to double-check my work.  Starting with Day 09, I have begun implementing unit tests that directly leverage the problem description's worked example printouts (example), which has sped up my problem solving and gives me assurance that I'm on the right track.

## I'm particularly proud of several solutions!

(link to READMEs)

- Day 08 (Treetop Tree House)
    - In addition to solving parts one/two, also created command-prompt animation!
- Day 09 (Rope Bridge)
    - First started implementing unit testing (using Python's `unittest` module) - big help in understanding the problem.
- [Day 11 (Monkey in the Middle)](/day11/)
    - Learned some basic `numpy` for optimization and modular arithmetic for solving the problem - part two was hard!

## General problem structure & my problem solving strategies

### Input text file -> internal program state
. input from text file -> internal state  (show an example!)
    . use combination of simple classes / data structures to represent puzzle elements
    . sometimes use regex to parse input file

### Simulation and calculation
. simulate change(s), calculate something
    . Predicting what'll change from parts 1 -> 2
        . if multiple rounds of simulation are involved - try to make function that simulates a single cycle (or n cycles) given input state and outputs final state
    . making parameterized functions

### Unit testing
. unit testing to validate against example(s) given in problem description
    . give specific example -- day09 rope simulation!