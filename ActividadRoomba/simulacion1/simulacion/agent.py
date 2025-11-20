"""
Author: Juan de Dios Gastélum Flores - A01784523
Date: 19-11-2025
Description: Agent definitions for the Roomba simulation.
"""

from mesa.discrete_space import CellAgent, FixedAgent
import heapq

class Obstacle(FixedAgent):
    """
    Agent representing an obstacle in the environment.
    Roombas cannot move into cells occupied by these agents.
    """
    def __init__(self, model, cell):
        """
        Initializes the obstacle.
        Args:
            model: Reference to the simulation model.
            cell: The cell where the obstacle is located.
        """
        super().__init__(model)
        self.cell = cell

    def step(self):
        """
        Obstacles are static and perform no actions.
        """
        pass

class Dirt(FixedAgent):
    """
    Agent representing dirt or trash in a cell.
    """
    def __init__(self, model, cell):
        """
        Initializes the dirt.
        Args:
            model: Reference to the simulation model.
            cell: The cell where the dirt is located.
        """
        super().__init__(model)
        self.cell = cell

    def step(self):
        """
        Dirt is static until cleaned.
        """
        pass

class ChargingStation(FixedAgent):
    """
    Agent representing a charging station.
    Allows the Roomba to recharge its battery.
    """
    def __init__(self, model, cell):
        """
        Initializes the charging station.
        Args:
            model: Reference to the simulation model.
            cell: The cell where the station is located.
        """
        super().__init__(model)
        self.cell = cell

    def step(self):
        """
        Charging stations are static.
        """
        pass

class Roomba(CellAgent):
    """
    Robot agent that cleans the room.
    It uses a subsumption architecture to decide its actions:
    1. Charge battery (if low and at station).
    2. Return to station (if battery is low).
    3. Clean (if the current cell is dirty).
    4. Explore (move randomly).
    """
    def __init__(self, model, cell):
        """
        Initializes the Roomba agent.
        Args:
            model: Reference to the simulation model.
            cell: The starting cell of the agent.
        """
        super().__init__(model)
        self.cell = cell 
        self.batteryLevel = 100
        self.batteryThreshold = 20

    def step(self):
        """
        Executes one step of the agent's behavior using subsumption architecture.
        Priorities:
        1. Survival (Charging/Going to Station)
        2. Work (Cleaning)
        3. Exploration (Random movement)
        """
        # Priority 1: Survival - Check if charging is needed
        if self.batteryLevel < 100 and self.isAtChargingStation():
            self.chargeBattery()
        elif self.batteryLevel < self.batteryThreshold:
            self.moveToNearestStation()
        
        # Priority 2: Work - Check if current cell is dirty
        elif self.isCellDirty():
            self.cleanCell()
        
        # Priority 3: Exploration - Move randomly if no other priority is active
        else:
            self.moveRandomly()

    def isAtChargingStation(self):
        """
        Checks if the agent is currently at a charging station.
        Returns:
            True if at a station, False otherwise.
        """
        agentsInCell = self.cell.agents
        isAtStation = False
        for agent in agentsInCell:
            if isinstance(agent, ChargingStation):
                isAtStation = True
        return isAtStation

    def chargeBattery(self):
        """
        Recharges the agent's battery.
        Adds 5% per step, up to a maximum of 100%.
        """
        self.batteryLevel += 5
        if self.batteryLevel > 100:
            self.batteryLevel = 100

    def isCellDirty(self):
        """
        Checks if the current cell contains a Dirt agent.
        Returns:
            True if dirt is present, False otherwise.
        """
        agentsInCell = self.cell.agents
        hasDirt = False
        for agent in agentsInCell:
            if isinstance(agent, Dirt):
                hasDirt = True
        return hasDirt

    def cleanCell(self):
        """
        Cleans the dirt in the current cell.
        Consumes 1% battery.
        """
        agentsInCell = self.cell.agents
        dirtAgent = None
        for agent in agentsInCell:
            if isinstance(agent, Dirt) and dirtAgent is None:
                dirtAgent = agent
        
        if dirtAgent is not None:
            dirtAgent.remove() 
            self.batteryLevel -= 1

    def moveRandomly(self):
        """
        Moves the agent to a random accessible neighbor cell.
        Consumes 1% battery.
        """
        neighbors = self.cell.neighborhood
        validNeighbors = []
        
        for neighbor in neighbors:
            isObstacle = False
            for agent in neighbor.agents:
                if isinstance(agent, Obstacle):
                    isObstacle = True
            
            if not isObstacle:
                validNeighbors.append(neighbor)

        if len(validNeighbors) > 0:
            nextCell = self.random.choice(validNeighbors)
            self.cell = nextCell
            self.batteryLevel -= 1

    def moveToNearestStation(self):
        """
        Uses Dijkstra's algorithm to find the path to the nearest charging station
        and moves one step towards it.
        Consumes 1% battery.
        """
        targetCells = []
        
        for agent in self.model.agents:
            if isinstance(agent, ChargingStation):
                targetCells.append(agent.cell)
        
        if len(targetCells) > 0:
            nextStep = self.dijkstraNextStep(self.cell, targetCells)
            
            if nextStep is not None and nextStep != self.cell:
                self.cell = nextStep
                self.batteryLevel -= 1

    def dijkstraNextStep(self, startCell, targetCells):
        """
        Implements Dijkstra's algorithm to find the shortest path.
        Args:
            startCell: The starting cell (Cell object).
            targetCells: A list of possible destination cells (Cell objects).
        Returns:
            The next Cell object in the optimal path.
        """
        priorityQueue = []
        heapq.heappush(priorityQueue, (0, id(startCell), startCell))
        
        cameFrom = {} 
        costSoFar = {}
        
        cameFrom[startCell] = None
        costSoFar[startCell] = 0
        
        closestTarget = None
        targetFound = False
        
        while len(priorityQueue) > 0 and not targetFound:
            currentTuple = heapq.heappop(priorityQueue)
            currentCell = currentTuple[2]
            
            isTarget = False
            for target in targetCells:
                if currentCell == target:
                    isTarget = True
            
            if isTarget:
                closestTarget = currentCell
                targetFound = True
            else:
                neighbors = currentCell.neighborhood
                for neighbor in neighbors:
                    isObstacle = False
                    for agent in neighbor.agents:
                        if isinstance(agent, Obstacle):
                            isObstacle = True
                    
                    if not isObstacle:
                        newCost = costSoFar[currentCell] + 1 
                        
                        if neighbor not in costSoFar or newCost < costSoFar[neighbor]:
                            costSoFar[neighbor] = newCost
                            priorityQueue.append((newCost, id(neighbor), neighbor))
                            heapq.heapify(priorityQueue) 
                            cameFrom[neighbor] = currentCell
        
        nextStep = None
        if closestTarget is not None:
            current = closestTarget
            isStart = (current == startCell)
            while not isStart:
                previous = cameFrom[current]
                if previous == startCell:
                    nextStep = current
                    isStart = True
                else:
                    current = previous
                    
        return nextStep