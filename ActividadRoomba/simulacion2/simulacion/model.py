"""
Author: Juan de Dios Gastélum Flores - A01784523
Date: 19-11-2025
Description: RoombaModel class for Simulation 2 (Multi-Agent).
"""

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import OrthogonalMooreGrid
from .agent import Roomba, Obstacle, Dirt, ChargingStation

class RoombaModel(Model):
    """
    Model class for the Multi-Agent Roomba simulation.
    """
    def __init__(self, width, height, numAgents, dirtPercentage, obstaclePercentage, maxTime):
        """
        Initializes the simulation model.
        
        Args:
            width: Grid width.
            height: Grid height.
            numAgents: Number of Roombas (and charging stations).
            dirtPercentage: Percentage of dirty cells.
            obstaclePercentage: Percentage of obstacle cells.
            maxTime: Max steps.
        """
        super().__init__()
        self.numAgents = numAgents
        self.grid = OrthogonalMooreGrid((width, height), torus=False, random=self.random)
        self.running = True
        self.maxTime = maxTime
        self.stepCount = 0

        totalCells = width * height
        numObstacles = int(totalCells * obstaclePercentage)
        numDirt = int(totalCells * dirtPercentage)

        # --- Agent & Station Placement ---      
        for i in range(self.numAgents):

            pos_cell = self.find_valid_start_cell()
            
            if pos_cell:
                ChargingStation(self, pos_cell)

                Roomba(self, pos_cell, unique_id=f"Roomba_{i}")

        # --- Obstacle Placement ---
        obstaclesPlaced = 0
        while obstaclesPlaced < numObstacles:
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            cell = self.grid[(x, y)]
            
            if cell.is_empty:
                Obstacle(self, cell)
                obstaclesPlaced += 1

        # --- Dirt Placement ---
        dirtPlaced = 0
        while dirtPlaced < numDirt:
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            cell = self.grid[(x, y)]

            if cell.is_empty:
                Dirt(self, cell)
                dirtPlaced += 1

        # --- Data Collection ---
        self.datacollector = DataCollector(
            model_reporters={
                "CleanPercentage": self.getCleanPercentage,
                "DirtyCells": lambda m: m.countDirt(),
                "Steps": lambda m: m.stepCount
            },
            agent_reporters={
                "StepsTaken": lambda a: a.steps_taken if isinstance(a, Roomba) else 0,
                "CellsCleaned": lambda a: a.cleaned_cells if isinstance(a, Roomba) else 0,
                "Battery": lambda a: a.batteryLevel if isinstance(a, Roomba) else 0
            }
        )
        
        self.datacollector.collect(self)

    def step(self):
        """
        Advances the model by one step.
        """
        self.stepCount += 1
        
        self.agents.shuffle_do("step")
        
        self.datacollector.collect(self)

        if self.countDirt() == 0 or self.stepCount >= self.maxTime:
            self.running = False

    def find_valid_start_cell(self):
        """
        Finds a random cell that is currently empty of any agents.
        Retries until valid or gives up.
        """
        for _ in range(100):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            cell = self.grid[(x, y)]
            
            if cell.is_empty:
                return cell
        return None

    def countDirt(self):
        """Counts Dirt agents using self.agents"""
        count = 0
        for agent in self.agents:
            if isinstance(agent, Dirt):
                count += 1
        return count

    def countObstacles(self):
        """Counts Obstacle agents using self.agents"""
        count = 0
        for agent in self.agents:
            if isinstance(agent, Obstacle):
                count += 1
        return count

    @staticmethod
    def getCleanPercentage(model):
        totalCells = model.grid.width * model.grid.height
        obstacles = model.countObstacles()
        dirt = model.countDirt()
        
        cleanableCells = totalCells - obstacles
        
        if cleanableCells > 0:
            cleanCells = cleanableCells - dirt
            return (cleanCells / cleanableCells) * 100
        else:
            return 100.0