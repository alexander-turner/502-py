import castle as cstl
from copy import copy
import numpy as np
import tabulate


class CastleDealer:
    def run(self, max_height, max_width):
        """Initializes bounds so we know up to what point cached moves should be prepared.

        :param max_height: the maximum Castle height that will be used
        :param max_width: the maximum Castle width that will be used
        """
        self.max_height, self.max_width = max_height, max_width

        self.cache_moves()
        self.castle_results = {}  # castle_results[castle] = number of even- and odd-blocked solutions

        self.iterate_castles()

    def cache_moves(self):  # todo generate on fly
        # cached_moves[i] contains the moves available for a space of size i that weren't available for k < i
        self.cached_moves = [[] for _ in range(self.max_width + 1)]
        for move_size in range(1, self.max_width + 1):  # each valid size
            for move_index in range(self.max_width + 1 - move_size):  # each valid index
                self.cached_moves[move_size].append(cstl.Block(move_index, move_size))

    def iterate_castles(self):
        """Iterate Castles up to (max_height, max_width) and display results."""
        print("Iterating over castle sizes (dimensions not exceeding {} by {}).".format(self.max_height,
                                                                                        self.max_width))
        print("Results format: [solutions with even blocks, solutions with odd blocks]")

        table = []
        for width in range(1, self.max_width + 1):
            new_row = [width]
            for height in range(1, self.max_height + 1):
                # Since all operations are reversible, just one global Castle can be used (for depth-first)
                self.castle = cstl.Castle(height, width)  # TODO fix confusing reversal?
                """
                For castles with height = 1, the result is {0, 1}.
                For castles where width = 1, the result is {(height + 1) % 2, height % 2}.
                """
                result = self.solve_castle(0)
                new_row.append(result)
                self.castle_results[self.castle] = result

            table.append(new_row)
        headers = ["width \ height"]
        headers += list(range(1, self.max_height + 1))
        print(tabulate.tabulate(table, headers, tablefmt="grid"))

    def solve_castle(self, start_index):
        """Recursively enumerate Castles.

        :param start_space_index: castle.spaces[castle.current_row][start_space_index] is currently being operated on.
        :return result: list containing the number of even- and odd-block-numbered castles matching the given criteria.
        """
        result = np.array([0, 0])

        if self.castle.last_row_has_blocks():
            # Mark how solutions are distributed across number of blocks used
            result[0 if self.castle.last_id_even() else 1] += 1

        if self.castle.can_add_block():
            for space_index, space in enumerate(self.castle.spaces[self.castle.current_row][start_index:],
                                                start=start_index):  # for each remaining space
                for move_width in range(1, space.width + 1):
                    for move_index in range(space.width - move_width):
                        move = copy(self.cached_moves[move_width][move_index])
                        move.index += space.index  # increment by current index; cached_moves doesn't account for offset

                        last_space_index = self.castle.place_block_update(move, space_index)

                        if self.castle.skip_space:  # leave current space alone and proceed to next in list (branching)
                            self.castle.skip_space = False
                            result += self.solve_castle(last_space_index + 1)
                        else:
                            result += self.solve_castle(last_space_index)

                        self.castle.remove_block_update(move, last_space_index)

        if self.castle.can_advance():
            self.castle.advance_row()
            result += self.solve_castle(0)
            self.castle.retreat_row()

        return result
