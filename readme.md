# [Project Euler Problem 502](https://projecteuler.net/problem=502)

>A block is defined as a rectangle with a height of 1 and an integer-valued length. Let a castle be a configuration of stacked blocks.

>Given a game grid that is `w` units wide and `h` units tall, a castle is generated according to the following rules:
1. Blocks can be placed on top of other blocks as long as nothing sticks out past the edges or hangs out over open space.
2. All blocks are aligned/snapped to the grid.
3. Any two neighboring blocks on the same row have at least one unit of space between them.
4. The bottom row is occupied by a block of length `w`.
5. The maximum achieved height of the entire castle is exactly `h`.
6. The castle is made from an even number of blocks.

> Let `F(w, h)` represent the number of valid castles, given grid parameters w and h.
For example, `F(4, 2) = 10`, `F(13, 10) = 3,729,050,610,636`, `F(10, 13) = 37,959,702,514`, and `F(100, 100) mod 1,000,000,007 =
841,913,936`.

## Synopsis
This problem deals with finding permutations on a `w x h` grid that meet a precise
set of criteria. My proposed solution is wholly inadequate for finding `(F(1,012, 100) + F(10,000,
10,000) + F(100, 1,012)) mod 1,000,000,007`; to my mind, no computational optimization would suffice. Due to the exponential nature
of the castle's state space, I suspect that an equation is required. This solution could even be recursive (à la
Fibonnaci Sequence). However, all of my attempts to derive an equation thus far for widths / heights greater than 3 have
failed. This program is thus an exploration of the concept space in hopes of obtaining a better understanding.


## Proposed Solution
The basic idea is to start from a blank slate (dimensions: `3 x 3`; ▓ := unavailable open space):

░░░

░░░

███

and pursue each option:

░░░ ░░▓ ▓░░ ░▓░ ▓░▓ ░▓░

███ ██▓ ▓██ █▓░ ▓█▓ ░▓█

███ ███ ███ ███ ███ ███

After every move, we check to see if the current configuration satisfies the 6 criteria listed above.
If it does, we add it to the sum for the current iteration of the function, which is eventually returned and
added to those found by the other branches in the depth-first search.