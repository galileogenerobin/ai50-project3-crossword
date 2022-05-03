import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Loop through each variable and update its domains
        for var in self.domains:
            # Loop through each word in the domain and remove it if it doesn't match the variable's length
            for word in self.domains[var]:
                if len(word) != var.length:
                    self.domains[var].remove(word)
        # raise NotImplementedError

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        # Check if there are no overlaps, then no need to revise
        if self.crossword.overlaps[x, y] is None:
            return revised

        # If there is an overlap, get the index values
        x_index, y_index = self.crossword.overlaps[x, y]

        # Loop through all existing values in the domain of x
        for x_word in self.domains[x]:
            # Check the words in the domain of y that is consistent with the current word
            consistent_words = [y_word for y_word in self.domains[y] if x_word[x_index] == y_word[y_index]]
            # If no consistent words, remove the word from x's domain and set revised to True
            if len(consistent_words) == 0:
                self.domains[x].remove[x_word]
                revised = True

        return revised
        # raise NotImplementedError

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Create a queue of arcs
        if arcs:
            queue = arcs
        else:
            # If no list of arcs provided, create the queue from all arcs (combination of variables with overlaps)
            queue = []
            for v1 in self.domains:
                for v2 in self.domains:
                    if v1 == v2 or self.crossword.overlaps[v1, v2] == None:
                        continue
                    queue.append((v1, v2))

        # Now that our queue is ready, we start with enforcing arc consistency on our arcs
        while len(queue) > 0:
            x, y = queue.pop(0)
            # If there are changes to the domain of the x to make arc consistent with y
            if self.revise(x, y):
                # If, after enforcing arc consistency, the domains of x is empty, return False, i.e. no solution
                if self.domains[x] == set():
                    return False
                # Add to the queue all neighbors of x (except y) to recheck arc consistency
                for z in (self.crossword.neighbors(x) - {y}):
                    queue.append((z, x))

        # After going through all arcs and each variable still has values in its domain, we have enforced arc consistency
        return True
        # raise NotImplementedError

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Iterate through all variables in the assignment and check that each has an assigned value
        for val in assignment.values():
            # Check that each cell in the variable has a value
            if val is None:
                return False

        return True
        # raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Iterate through all variables in the assignment and check consistency with its neighbors
        for v1 in assignment:
            word = assignment[v1]
            # If no assigned value yet, skip this variable
            if not word:
                continue
            
            # If with assigned value...
            # ... 1. check if duplicate value exists in assignment
            # We do this by getting the list of values in 'assignment', and calling the count function
            if list(assignment.values()).count(word) > 1:
                return False
            # ... 2. check if value is of correct length
            if len(assignment[v1]) != v1.length:
                return False

            # ... 3. check neighbors
            neighbors = self.crossword.neighbors(v1)
            if neighbors:
                for v2 in neighbors:
                    word2 = assignment[v2]
                    # For each neighbor, check if a word has been assigned; if so, check overlapping values
                    if word2:
                        i, j = self.crossword.overlaps[v1, v2]
                        if word[i] != word2[j]:
                            # If overlapping values are not the same, return False
                            return False

        # If, after going through all variables, no inconsistencies were found, return True
        return True
        # raise NotImplementedError

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Check if assignment is complete
        if self.assignment_complete(assignment):
            return assignment

        # Select an unassigned variable
        var = self.select_unassigned_variable(assignment)
        
        # Iterate through all words from the variable domain
        for word in self.order_domain_values(var, assignment):
            # Create a copy of the assignment
            new_assignment = assignment.copy()
            # Assign the word to the variable
            new_assignment[var] = word
            # Check if new assignment is consistent
            if self.consistent(new_assignment):
                # If consistent, recursively assign more variables; if no inconsistency found along the way, return result
                result = self.backtrack(new_assignment)
                if result:
                    return result
                # Since we created a copy of the assignment above, no need to manually revert the assignment when we backtrack

        # If the assignment was not completed along the way for all words, return None
        return None
        # raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
