"""
Author: Juan de Dios Gastélum Flores - A01784523
Date: 19-11-2025
Description: Agent definitions for Roomba Simulation 2 (Multi-Agent).
"""

from mesa.discrete_space import CellAgent, FixedAgent
import heapq

class Obstacle(FixedAgent):
    """
    Agent representing an obstacle in the environment.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell

    def step(self):
        pass

class Dirt(FixedAgent):
    """
    Agent representing dirt in a cell.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell

    def step(self):
        pass

class ChargingStation(FixedAgent):
    """
    Agent representing a charging station.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell

    def step(self):
        pass

class Roomba(CellAgent):
    """
    Robot agent that cleans the room.
    Tracks individual statistics: steps taken and cells cleaned.
    """
    def __init__(self, model, cell, unique_id):
        """
        Args:
            model: The simulation model.
            cell: The starting Cell object.
            unique_id: Unique identifier for data collection.
        """
        super().__init__(model)
        self.cell = cell
        self.unique_id = unique_id 
        
        self.batteryLevel = 100
        self.batteryThreshold = 20
        
        self.steps_taken = 0
        self.cleaned_cells = 0

    def step(self):
        """
        Executes one step of the agent's behavior.
        """
        # Priority 1: Charge if at station and needed
        if self.isAtChargingStation() and self.batteryLevel < 100:
            self.chargeBattery()
        
        # Priority 2: Return to station if battery is low
        elif self.batteryLevel < self.batteryThreshold:
            self.moveToNearestStation()
        
        # Priority 3: Clean if dirty
        elif self.isCellDirty():
            self.cleanCell()
        
        # Priority 4: Move randomly
        else:
            self.moveRandomly()
        
        self.steps_taken += 1

    def isAtChargingStation(self):
        """
        Checks if the current cell has a ChargingStation.
        """
        is_at_station = False
        for agent in self.cell.agents:
            if isinstance(agent, ChargingStation):
                is_at_station = True
        return is_at_station

    def chargeBattery(self):
        """
        Charges battery by 5% per step.
        """
        self.batteryLevel += 5
        if self.batteryLevel > 100:
            self.batteryLevel = 100

    def isCellDirty(self):
        """
        Checks if the current cell has Dirt.
        """
        is_dirty = False
        for agent in self.cell.agents:
            if isinstance(agent, Dirt):
                is_dirty = True
        return is_dirty

    def cleanCell(self):
        """
        Removes Dirt agent from the current cell.
        Updates cleaned_cells metric.
        """
        dirt_agent = None
        for agent in self.cell.agents:
            if isinstance(agent, Dirt) and dirt_agent is None:
                dirt_agent = agent
        
        if dirt_agent is not None:
            dirt_agent.remove()
            self.batteryLevel -= 1
            self.cleaned_cells += 1

    def moveRandomly(self):
        """
        Moves to a random neighbor that is not an Obstacle.
        """
        valid_neighbors = []
        for neighbor in self.cell.neighborhood:
            is_obstacle = False
            for agent in neighbor.agents:
                if isinstance(agent, Obstacle):
                    is_obstacle = True
            
            if not is_obstacle:
                valid_neighbors.append(neighbor)

        if len(valid_neighbors) > 0:
            next_cell = self.random.choice(valid_neighbors)
            self.cell = next_cell
            self.batteryLevel -= 1

    def moveToNearestStation(self):
        """
        Uses Dijkstra to find the nearest charging station and moves towards it.
        """
        target_cells = []
        for agent in self.model.agents:
            if isinstance(agent, ChargingStation):
                target_cells.append(agent.cell)
        
        if len(target_cells) > 0:
            next_step = self.dijkstraNextStep(self.cell, target_cells)
            
            if next_step is not None and next_step != self.cell:
                self.cell = next_step
                self.batteryLevel -= 1
        else:
            self.moveRandomly()

    def dijkstraNextStep(self, start_cell, target_cells):
        """
        Standard Dijkstra algorithm to find the next step towards the closest target.
        """
        pq = []
        heapq.heappush(pq, (0, id(start_cell), start_cell))
        
        came_from = {start_cell: None}
        cost_so_far = {start_cell: 0}
        closest_target = None
        target_found = False
        
        while len(pq) > 0 and not target_found:
            current_cost, _, current_cell = heapq.heappop(pq)
            
            is_target = False
            for target in target_cells:
                if current_cell == target:
                    is_target = True
            
            if is_target:
                closest_target = current_cell
                target_found = True
            else:
                if current_cost < 50: 
                    for neighbor in current_cell.neighborhood:
                        is_obstacle = False
                        for agent in neighbor.agents:
                            if isinstance(agent, Obstacle):
                                is_obstacle = True
                        
                        if not is_obstacle:
                            new_cost = cost_so_far[current_cell] + 1
                            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                                cost_so_far[neighbor] = new_cost
                                heapq.heappush(pq, (new_cost, id(neighbor), neighbor))
                                came_from[neighbor] = current_cell
        
        next_step = None
        if closest_target is not None:
            curr = closest_target
            is_start = (curr == start_cell)
            
            while not is_start:
                prev = came_from[curr]
                if prev == start_cell:
                    next_step = curr
                    is_start = True
                else:
                    curr = prev
                    if curr is None:
                        is_start = True

        return next_step