# FixedAgent: Immobile agents permanently fixed to cells
from mesa.discrete_space import FixedAgent

class Cell(FixedAgent):
    """Represents a single ALIVE or DEAD cell in the simulation."""

    DEAD = 0
    ALIVE = 1

    @property
    def x(self):
        return self.cell.coordinate[0]

    @property
    def y(self):
        return self.cell.coordinate[1]

    @property
    def is_alive(self):
        return self.state == self.ALIVE

    @property
    def neighbors(self):
        return self.cell.neighborhood.agents
    
    def __init__(self, model, cell, init_state=DEAD):
        """Create a cell, in the given state, at the given x, y position."""
        super().__init__(model)
        self.cell = cell
        self.pos = cell.coordinate
        self.state = init_state
        self._next_state = None

    def upper_neighbors(self):
        """Return the values 0/1 of the three upper neighbors."""
        left = 0
        center = 0
        right = 0
        high_y = self.y + 1 # Fila superior

        for n in self.neighbors: # Recorremos los vecinos
            if n.y == high_y: # Si el vecino está en la fila superior
                if n.x == self.x - 1: # Vecino izquierdo
                    left = 1 if n.is_alive else 0 # Asignamos 1 si está vivo, 0 si está muerto
                elif n.x == self.x: # Vecino central
                    center = 1 if n.is_alive else 0 # Asignamos 1 si está vivo, 0 si está muerto
                elif n.x == self.x + 1: # Vecino derecho
                    right = 1 if n.is_alive else 0 # Asignamos 1 si está vivo, 0 si está muerto
        return (left, center, right)

    def determine_state(self):
        """Compute if the cell will be dead or alive at the next tick.  This is
        based on the number of alive or dead neighbors.  The state is not
        changed here, but is just computed and stored in self._nextState,
        because our current state may still be necessary for our neighbors
        to calculate their next state.
        """
        # Get the neighbors and apply the rules on whether to be alive or dead
        # at the next tick.
        if self.y == self.model.grid.height - 1:
            self._next_state = self.state
            return

        vals = self.upper_neighbors() # Valores de los vecinos superiores
        key = str(vals[0]) + str(vals[1]) + str(vals[2]) # Cadena para ver su estado

        # A partir de la cadena genera el siguiente estado
        if key == "111":
            out = 0
        elif key == "110":
            out = 1
        elif key == "101":
            out = 0
        elif key == "100":
            out = 1
        elif key == "011":
            out = 1
        elif key == "010":
            out = 0
        elif key == "001":
            out = 1
        else:
            out = 0

        # Actualizamos estado
        if out == 1:
            self._next_state = self.ALIVE
        else:
            self._next_state = self.DEAD

    def assume_state(self):
        """Set the state to the new computed state -- computed in step()."""
        self.state = self._next_state