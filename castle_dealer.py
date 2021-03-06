from castle import Block, Castle
import numpy as np
import tabulate


class CastleDealer:
    def run(self, max_width, max_height):
        """Iterates Castles up to (max_height, max_width) and displays results.

        :param max_width: the maximum Castle width that will be used
        :param max_height: the maximum Castle height that will be used
        """
        print("Iterating over castle sizes (dimensions not exceeding {} by {}).".format(max_width, max_height))

        table = []
        for width in range(1, max_width + 1):
            new_row = [width]
            for height in range(1, max_height + 1):
                self.castle = Castle(width, height) # all operations are reversible; use one global Castle
                new_row.append(self.solve_castle(0))
            table.append(new_row)

        print("Results format: [solutions with even blocks, solutions with odd blocks]")
        headers = ["width \ height"] + list(range(1, max_height + 1))
        print(tabulate.tabulate(table, headers, tablefmt="grid"))

    def solve_castle(self, start_index):
        """Recursively enumerate Castles.

        When height = 1, the result is [0, 1].
        When width = 1, the result is [(height + 1) % 2, height % 2].

        :param start_index: castle.spaces[castle.current_row][start_space_index] is currently being operated on.
        :return result: list containing the number of even- and odd-block-numbered castles matching the given criteria.
        """
        result = np.array([0, 0])

        if self.castle.last_row_has_blocks():
            result[1 if self.castle.last_id_even() else 0] += 1

        if self.castle.can_add_block():
            for space_index, space in enumerate(self.castle.spaces[self.castle.current_row][start_index:],
                                                start=start_index):  # for each remaining space
                for move_width in range(1, space.width + 1):
                    for move_index in range(space.index, space.index + space.width - move_width + 1):
                        move = Block(move_index, move_width)
                        last_space_index = self.castle.place_block(move, space_index)

                        if self.castle.skip_space:  # leave current space alone and proceed to next in list (branching)
                            self.castle.skip_space = False
                            result += self.solve_castle(last_space_index + 1)
                        else:
                            result += self.solve_castle(last_space_index)

                        self.castle.remove_block(move, last_space_index)

        if self.castle.can_advance():
            self.castle.advance_row()
            result += self.solve_castle(0)
            self.castle.retreat_row()

        return result
