"""
Author: Juan de Dios Gastélum Flores - A01784523
Date: 19-11-2025
"""

from mesa.visualization import Slider, SolaraViz, make_space_component, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle
from simulacion.model import RoombaModel
from simulacion.agent import Roomba, Obstacle, Dirt, ChargingStation

def agent_portrayal(agent):
    """
    Defines how agents are rendered in the Solara visualization.
    Args:
        agent: The agent to render.
    Returns:
        AgentPortrayalStyle: The visual style for the agent.
    """
    if agent is None:
        return

    portrayal = AgentPortrayalStyle(
        size=50,
        marker="o", 
        color="black"
    )

    if isinstance(agent, Roomba):
        portrayal.color = "tab:blue"
        portrayal.size = 80
        portrayal.marker = "o"
        
    elif isinstance(agent, Dirt):
        portrayal.color = "tab:brown"
        portrayal.size = 40
        portrayal.marker = "s"

    elif isinstance(agent, Obstacle):
        portrayal.color = "black"
        portrayal.size = 90
        portrayal.marker = "s"

    elif isinstance(agent, ChargingStation):
        portrayal.color = "tab:green"
        portrayal.size = 100
        portrayal.marker = "P"

    return portrayal

model_params = {
    "numAgents": Slider("Number of Agents", 1, 1, 5, 1),
    "width": Slider("Grid Width", 10, 5, 20, 1),
    "height": Slider("Grid Height", 10, 5, 20, 1),
    "dirtPercentage": Slider("Dirt Percentage", 0.3, 0.0, 1.0, 0.05),
    "obstaclePercentage": Slider("Obstacle Percentage", 0.2, 0.0, 1.0, 0.05),
    "maxTime": Slider("Max Time Steps", 1000, 100, 5000, 100),
}

space_component = make_space_component(
    agent_portrayal,
    post_process=lambda ax: ax.set_aspect("equal"),
    draw_grid=True
)

plot_component = make_plot_component(
    {
        "CleanPercentage": "tab:green",
        "DirtyCells": "tab:brown",
        "TotalMoves": "tab:blue",
    }
)

initial_model = RoombaModel(
    width=10,
    height=10,
    numAgents=1,
    dirtPercentage=0.3,
    obstaclePercentage=0.2,
    maxTime=1000
)

page = SolaraViz(
    initial_model,
    components=[space_component, plot_component],
    model_params=model_params,
    name="Roomba Simulation 1 (Single Agent)"
)