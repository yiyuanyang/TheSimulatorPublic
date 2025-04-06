# Market Simulation

## The Simulation Engine

This is an implementation of an agent based simulation engine. Requires python 3.11 to run

### Core Simulation Logic

Located under ```SimulatorEngine/simulator_base```, it defines various driving objects for the simulation such as the orchestrator (progress time and run simulation on all objects in sequential manner), and other basic objects such as environment, event, effect, agent, actions and states.

## Ad Tech Simulation

Located under ```SimulatorEngine/market_simulation```, it builds derived objects of the base objects from the core simulator. It enables the simulation of the ad tech market with arbitrary number of users and advertisers on various different surfaces.

### How to run the simulation?

After setting up python environment and install packages from ```requirements.txt```. Just run ```python main.py``` under ```SimulatorEngine```.

Metrics on the simulation would be saved under ```SimulatorEngine/analytics``` with each simulation having its own folder. However, without changing the config and random seed, each run would yield exact same results.

### How to customize the simulation?

In ```SimulatorEngine/global_config.yaml```, we have random seed, simulation speed, where to send the analytics results, and various configurations for the core simulation logic.

In ```market_simulation/config/market_config.yaml```, we have the whole range of configurations that sets up the available surfaces, number of users, number of advertisers, their intents and various other things.

### What Are Simulated Here?

#### User

* User have fixed monthly income and disposable income / savings. This would affect their purchase decision.
* Country, Age, Gender as well as personal category interest that affects their purchase intent.
* They aren't always active at every second, not every user would come online every day.
* They ask for content every once in a while, and they would view a number of ads (from time they stay multiplied by a time based ad load) with a probability to convert.
* Seeing awareness ads improve their likelihood of converting on the same advertiser in the future, and seeing normal conversion ad repeatedly reduces their chance of converting on the advertiser.

#### Advertiser

* Advertiser has a daily budget that they can allocate to different ads.
* Advertiser can create awareness or conversion optimized ads that achieve different goal.
* Advertiser has a profit margin on the product as well as ROI they are looking for, if performance is lower than ROI they would.

#### Ad

* Each ad has a set of targeting / placement settings that has to be respected.
* Each ad has a daily budget that itself tries to pace. With goal of maximizing outcome while spending all of the budget at the end of the day if MAXIMIZE_OUTCOME_WITHOUT_COST_CAP selected.

#### Delivery System

* The delivery system is setup as a 3 stage system with a targeting stage (that retrieves only ads that satisfies the targeting filter), a ranking stage where probability is predicted and lastly an auction stage where all ads are ranked and priced based on second price.

## License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license.

You are free to use, modify, and share this code for **non-commercial purposes only**.

**Commercial use is not permitted** without explicit permission from the author.  
To request a commercial license, please contact me directly.

🔗 Full license text: [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)