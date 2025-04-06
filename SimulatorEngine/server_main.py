"""
    Server Main:

    Compared to main.py which is a server only version
    simulation. Server main is designed to be interactive
    with a client.
"""

from market_simulation.market_controller import MarketController
from flask import Flask

app = Flask(__name__)


@app.route("/setup")
def start_simulation():
    MarketController.get_instance()
    return "Simulation Initialized"


@app.route("/progress")
def tick():
    MarketController.get_instance().tick()


@app.route("/pause")
def pause():
    MarketController.get_instance().pause_simulation()


@app.route("/unpause")
def unpause():
    MarketController.get_instance().unpause_simulation()
