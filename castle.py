class Castle:
    """A robust interface for generating and manipulating Castles."""

    def __init__(self, height, width):
        self.width = width
        self.height = height
        self.block_grid = [[False] * self.width for _ in range(self.height)]  # Todo change to lists

        # Initialize record-keeping data-structures
        self.unavailable_column = [False] * self.width  # columns where we can't build without making an overhang
        self.placed_in_row = [0] * self.height
        self.spaces = [[] for _ in range(self.height)]  # spaces at each level of the castle
        
        self.last_id = 0  # ID of the last block placed
        self.current_row = self.height - 1  # current level we're working on todo invert
        # If we've already processed all permutations created by placing a block in space at space_index
        self.skip_space = False

        # Place first space and block
        self.spaces[self.current_row].append(Block(0, self.width))  # "block" of empty space
        self.place_block_update(Block(0, self.width), 0)

        # Leave the first row
        if self.can_advance():
            self.advance_row()

    def place_block_update(self, move, space_index):
        """ Robust block placement using constant-time space-navigation logic.

        :param move: a Block.
        :param space_index: the space currently being operated in is self.spaces[self.current_row][space_index].
        :return newIndex: index of left space created by the displacement move causes in the space. If no spaces remain,
            -1 is returned.
        """
        left_side, right_side = move.index - 1, move.index + move.width

        # Lay the block
        self.last_id += 1

        self.block_grid[self.current_row][move.index:right_side] = [True] * (right_side - move.index)
        self.placed_in_row[self.current_row] += 1

        # Mark sides as unavailable
        if left_side >= 0:
            self.unavailable_column[left_side] = True
        if right_side < self.width:
            self.unavailable_column[right_side] = True

        # Add a new space above, indicating that we can now build on top of the block
        self.modify_space_above(move, True)

        space = self.spaces[self.current_row].pop(space_index)  # question correct?

        # These tell us whether we have to perform additional book-keeping on spaces to the sides of the move
        modify_left = left_side > space.index
        modify_right = right_side + 1 < space.index + space.width  # if space ends past move's right end
        new_index = space_index

        # Modify the current row's spaces
        if modify_left:
            self.spaces[self.current_row].insert(space_index, Block(space.index, left_side - space.index))
            space_index += 1
            self.skip_space = True

        if modify_right:
            self.spaces[self.current_row].insert(space_index, Block(right_side + 1,
                                                                    space.index + space.width - right_side - 1))

        return new_index

    def remove_block_update(self, move, space_index):
        """Removes the specified already-placed block and merges any relevant space(s).

        :param move: a Block.
        :param space_index: the space in question in is self.spaces[self.current_row][space_index].
        """
        left_side, right_side = move.index - 1, move.index + move.width
        left_in_bounds, right_in_bounds = left_side > 0, right_side < self.width  # immediate neighbors in bounds?
        left_space_free, right_space_free = False, False  # is there a zero two spaces adjacent?
        block_to_left, block_to_right = False, False  # is there a block two spaces adjacent?
        left_overhang, right_overhang = False, False  # would building to left/right create an overhang?

        if left_in_bounds:  # TODO comment this
            left_overhang = not self.block_grid[self.current_row + 1][left_side]  # true if nothing is to the left
            if left_side > 0:
                block_to_left = self.block_grid[self.current_row][left_side - 1]
                left_space_free = not left_overhang and self.block_grid[self.current_row + 1][left_side - 1] and\
                                  not block_to_left and not self.unavailable_column[left_side - 1]

        if right_in_bounds:
            right_overhang = not self.block_grid[self.current_row + 1][right_side]
            if right_side < self.width - 1:
                block_to_right = self.block_grid[self.current_row][right_side + 1]
                right_space_free = not right_overhang and self.block_grid[self.current_row + 1][right_side + 1] and\
                                   not block_to_right and not self.unavailable_column[right_side + 1]

        increment_left = left_overhang or not left_in_bounds or (left_side > 0 and block_to_left)
        decrement_right = right_overhang or not right_in_bounds or (right_side < self.width - 1 and block_to_right)

        # Remove the block
        self.last_id -= 1
        self.block_grid[self.current_row][move.index:right_side] = [False] * (right_side - move.index)

        # Remove space above
        self.modify_space_above(move, False)
        self.placed_in_row[self.current_row] -= 1

        # Mark as available if the removed block was why the column wasn't available
        if left_in_bounds and not block_to_left and not left_overhang:
            self.unavailable_column[left_side] = False
        if right_in_bounds and not block_to_right and not right_overhang:
            self.unavailable_column[right_side] = False

        # Adjust dimensions of soon-to-be-added space
            if increment_left:
                left_side += 1
            if decrement_right:
                right_side -= 1

        # Increment width because if left bound == right bound == 0, it's a one-width block
        new_space = Block(left_side, right_side - left_side + 1)

        if left_space_free:  # todo comment and rename spaces
            space = self.spaces[self.current_row].pop(space_index)
            new_space = Block(space.index, new_space.width + space.width)

        if right_space_free:  # if open block to right, must be a space
            new_space.width += self.spaces[self.current_row][space_index].width
            self.spaces[self.current_row].pop(space_index)

        # Add the space
        self.spaces[self.current_row].insert(space_index, new_space)

    def modify_space_above(self, move, is_add):
        """Add or remove a space to/from the row above the given move. If already on the last row, does nothing.

        If a remove is desired, the space must be last in the list.

        :param move: Block object; the move being executed.
        :param is_add: is being called by an add operation.
        """
        above = self.current_row - 1  # todo fix when inverting
        if above < 0:
            return
        if is_add:
            self.spaces[above].append(Block(move.index, move.width))  # question can be move itself?
        else:
            self.spaces[above].pop()  # question ok to just pop here?

    def advance_row(self):
        self.current_row -= 1

    def retreat_row(self):
        self.current_row += 1

    def last_id_even(self):
        """True if the last block ID was even."""
        return ((self.last_id - 1) % 2) == 0  # question check

    def last_row_has_blocks(self):
        return self.placed_in_row[0] > 0  # todo fix when inverting

    def in_last_row(self):
        return self.current_row == 0

    def is_even_solution(self):
        return self.last_row_has_blocks() and self.last_id_even()

    def is_odd_solution(self):
        return self.last_row_has_blocks() and not self.last_id_even()

    def can_add_block(self):
        return len(self.spaces[self.current_row]) > 0

    def can_advance(self):
        """Can start building the next level of the Castle."""
        return not self.in_last_row() and self.placed_in_row[self.current_row] > 0

    def __hash__(self):
        return 0  # TODO implement


class Block:
    def __init__(self, index, width):
        """Demarcates the starting column and width of a block.

        :param index: column where the left edge of the space begins.
        :param width:
        """
        self.index = index
        self.width = width

    def __repr__(self):
        print("(index: {}, width: {})".format(self.index, self.width))
