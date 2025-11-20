"""
Author: Juan de Dios Gastélum Flores - A01784523
Date: 19-11-2025
"""

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import OrthogonalMooreGrid
from .agent import Roomba, Obstacle, Dirt, ChargingStation

class RoombaModel(Model):
    """
    Model class for the Roomba simulation (Single Agent).
    """
    def __init__(self, width, height, numAgents, dirtPercentage, obstaclePercentage, maxTime):
        """
        Initializes the simulation model.
        """
        super().__init__()
        self.numAgents = numAgents
        # Use OrthogonalMooreGrid which creates 'Cell' objects at each coordinate
        self.grid = OrthogonalMooreGrid((width, height), torus=False, random=self.random)
        self.running = True
        self.maxTime = maxTime
        self.stepCount = 0

        totalCells = width * height
        numObstacles = int(totalCells * obstaclePercentage)
        numDirt = int(totalCells * dirtPercentage)

        # --- Agent Placement ---

        # 1. Place Charging Station at [0,0] (Start Position)
        # Retrieve the actual Cell object at (0,0)
        start_cell = self.grid[(0, 0)]
        
        # Create and place the Station (Agent adds itself to the cell automatically)
        ChargingStation(self, start_cell)

        # 2. Place Roomba Agent at [0,0]
        Roomba(self, start_cell)

        # 3. Place Obstacles randomly
        obstaclesPlaced = 0
        while obstaclesPlaced < numObstacles:
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            cell = self.grid[(x, y)]

            # Check if cell is empty (Cell object property)
            if cell.is_empty and cell != start_cell:
                Obstacle(self, cell)
                obstaclesPlaced += 1

        # 4. Place Dirt randomly
        dirtPlaced = 0
        while dirtPlaced < numDirt:
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            cell = self.grid[(x, y)]

            # Ensure no obstacles, dirt, or station are in the cell
            if cell.is_empty and cell != start_cell:
                Dirt(self, cell)
                dirtPlaced += 1

        # --- Data Collection ---
        self.datacollector = DataCollector(
            model_reporters={
                "CleanPercentage": self.getCleanPercentage,
                "DirtyCells": lambda m: m.countDirt(),
                "TotalMoves": lambda m: m.stepCount
            }
        )
        
        # Collect initial state
        self.datacollector.collect(self)

    def step(self):
        """
        Advances the model by one step.
        """
        self.stepCount += 1
        
        # This shuffles the order and calls the 'step' method on each agent
        self.agents.shuffle_do("step")
        
        self.datacollector.collect(self)

        # Check termination conditions
        if self.countDirt() == 0 or self.stepCount >= self.maxTime:
            self.running = False

    def countDirt(self):
        """Counts Dirt agents currently in the model."""
        count = 0
        for agent in self.agents:
            if isinstance(agent, Dirt):
                count += 1
        return count

    def countObstacles(self):
        """Counts Obstacle agents currently in the model."""
        count = 0
        for agent in self.agents:
            if isinstance(agent, Obstacle):
                count += 1
        return count

    @staticmethod
    def getCleanPercentage(model):
        """
        Calculates the percentage of clean cells.
        """
        totalCells = model.grid.width * model.grid.height
        obstacles = model.countObstacles()
        dirt = model.countDirt()
        
        cleanableCells = totalCells - obstacles
        
        if cleanableCells > 0:
            cleanCells = cleanableCells - dirt
            return (cleanCells / cleanableCells) * 100
        else:
            return 100.0