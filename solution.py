assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    def is_naked_twins(b1, b2):
        if b1 == b2:
            return False
        return values[b1] == values[b2] and len(values[b1]) == 2

    all_naked_twins = []
    # Find all instances of naked twins
    for unit in unitlist:
        all_naked_twins += [(box1, box2, values[box1]) for box1 in unit for box2 in unit if
                           is_naked_twins(box1, box2)]

    # Eliminate the naked twins as possibilities for their peers
    for twins in all_naked_twins:
        common_peers = set(peers[twins[0]]).intersection(set(peers[twins[1]]))
        value = twins[2]
        for p in common_peers:
            assign_value(values, p, values[p].replace(value[0], ""))
            assign_value(values, p, values[p].replace(value[1], ""))

    return values


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diag_units = [[t[0] + t[1] for t in zip(rows, cols)]] + [[t[0] + t[1] for t in zip(rows, cols[::-1])]]
unitlist = row_units + column_units + square_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    return dict(zip(boxes, ['123456789' if x == '.' else x for x in grid]))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    resolvedBoxes = [x for x in values.keys() if len(values[x]) == 1]

    def removeFromPeers(k, v):
        for p in peers[k]:
            assign_value(values, p, values[p].replace(v, ""))

    for b in resolvedBoxes:
        removeFromPeers(b, values[b])

    return values

def only_choice(values):
    for unit in unitlist:
        counts = {}
        for d in '123456789':
            counts[d] = [box for box in unit if d in values[box]]
        for digit, boxes in counts.items():
            if len(boxes) == 1:
                assign_value(values, boxes[0], digit)

    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy
        eliminate(values)
        # Use the Only Choice Strategy
        only_choice(values)
        # Use the Naked Twins Strategy
        naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    values = reduce_puzzle(values)
    if values is False:
        return False

    if all(len(values[s]) == 1 for s in boxes):
        return values

    unfilled = [box for box in values.keys() if len(values[box]) > 1]
    selected_box = min(unfilled, key=lambda x: len(values[x]))
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    alternatives = list(values[selected_box])
    for value in alternatives:
        new_values = values.copy()
        assign_value(new_values, selected_box, value)
        answer = search(new_values)
        if answer:
            return answer
    return False

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '...7.2.4.........7217....9.6.......3.2..48..........1..5..........3.......6......'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
