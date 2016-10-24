Carrom_rl
=========

An open source Carrom Simulator interface for testing intelligent/learning agents.

[![Join the chat at https://gitter.im/Carrom_rl/Lobby](https://badges.gitter.im/Carrom_rl/Lobby.svg)](https://gitter.im/Carrom_rl/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)


## Introduction

This is the 1.0 release of Carrom_rl - A Carrom Simulator, which provides an interface that allows you to design agents that that play carrom. It is built in python, using pygame + pymunk. This is the course project for [CS 747 - Foundations of Intelligent and Learning Agents](https://www.cse.iitb.ac.in/~shivaram/teaching/cs747-a2016/index.html), taught by [Prof. Shivaram Kalyanakrishnan](https://www.cse.iitb.ac.in/~shivaram/) at IIT Bombay.

Please report bugs [here](https://github.com/samiranrl/Carrom_rl/issues), along with steps to reproduce it.

Feedback is welcome. Enjoy!

## Carrom

![Carrom Board](https://i.ytimg.com/vi/LvryHWCgK0s/maxresdefault.jpg)
Image Source: https://i.ytimg.com/vi/LvryHWCgK0s/maxresdefault.jpg

The high-level objective is to use a striker disk with a flick of the finger to sink the lighter carrom men/coins, into one of the corner pockets. A carrom set contains 19 coins in three distinct colors: 9 white and 9 black corresponding to player 1 and player 2 respectively, and red for the queen. To win, you must pocket your own nine coins and the queen before your opponent. (The first player may only pocket white)

The full description and list of rules and regulations can be found at http://www.carrom.org/

### Why Carrom? 

It is an exciting and challenging domain:

- The state space is continuous
- The action space is continuous, with added noise
- The agent must adhere to the rules of carrom
- In the two-player case, the agent must plan a strategy against an adversary
- In 2v2 Carrom you must cooperate with another agent

In short, it is a multi-agent adversarial game with continious state and action spaces, with noise added in the actions, with complex rules that cannot be intuited by the reward structure.

## Rules
We slightly modify the rules of the game.

### Single Player

<img src="Images/p1.gif" width="300" height="300">

The goal of single player carrom is to design an agent that clears the board as fast as possible, adhering to the following rules:

- The player is allowed to pocket white and black coins. Each coin pocketed increases your score by 1.
- You cannot pocket the queen unless you have pocketed another coin.
- The queen must be pocketed before the last coin.
- If all the coins are pocketed except the queen, one of the coins is taken out of the pocket and put in the center.
- After pocketing the queen, you must sink one of your pieces, thereby 'covering' it, into any pocket in the next shot, or she is returned to the center spot.
- If you pocket the queen along with another of your own piece, it is covered by default.
- A covered queen will increase your score by 3 points
- If the striker goes into the pocket, it counts as a foul. All the pocketed coins that turn are placed in the center. The score does not increase.

The simulation displays the current score of the player, and the time elapsed since the server was initialized.

### Doubles

<img src="Images/p2.gif" width="300" height="300">

The goal of doubles is to design an agent, that wins against an opponent in a game of carrom, adhering to the following rules:

- The player to start/break must target white coins only. The other player must target black. Players' score increases by 1 if they pocket their own coin. 
- You cannot pocket the queen unless you have pocketed another coin.
- If the player pockets the opponent's coin, it counts as a foul. All coins pocketed that turn are kept in the center, and the score does not increase.
- If all the coins are pocketed except the queen, the other player wins the match.
- If you manage to pocket all of your own coins, and the opponent pockets and covers the queen, you win the match.
- After pocketing the queen, you must sink one of your pieces, thereby 'covering' it, into any pocket in the next shot, or she is returned to the center spot.
- If you pocket the queen along with another of your own piece, it is covered by default.
- A covered queen will increase your score by 3 points
- If the striker goes into the hole, it counts as a foul. All the pocketed coins in that turn are placed in the center. The score does not increase.

The simulation displays the current score of player 1 and player 2, and the time elapsed since the server was initialized.

## The agent and the environment

We formally define the carrom environment in the reinforcement learning context.

### State

The State is a list of current coin positions (x,y) coordinates returned to the user, and the current score of the player. If a coin is not present, it is assumed to be pocketed in one of the previous strikes. The state also includes the current score of the player. An example of the state is:

```
"State={'White_Locations': [(400,368),(437,420), (372,428),(337,367), (402,332), (463,367), (470,437), (405,474), (340,443)], 'Red_Location': [(400, 403)], 'Score': 0, 'Black_Locations': [(433,385),(405,437), (365,390), (370,350), (432,350), (467,402), (437,455), (370,465), (335,406)]}"
```

It is returned in the form of a string to the agent, which must be parsed. The logic for parsing such a state is built in the sample agent for your reference. 

### Action

The action is a three dimentional vector: [position,angle,force]

- position: The legally valid x position of the striker on the board. Accepts floats in the range 0-1 (normalized, including boundaries). 0 is the extreme left legal position, and 1 is the extreme right. 
- angle : The angle gives the direction (in degrees), where you want to hit the striker. Accepts floats in the range -45 to 225 (including boundaries)
- force: The fractional force with which you want to hit the striker. Accepts floats between 0-1 (normalized, including boundaries). The maximum force makes the striker cover a distance of 3.5 times the width of the board, starting from the center at an angle of 0, striking the walls 4 times, and touching nothing else. There is a minimum force with which you strike (even if you pass 0)

The following examples demonstrate some shots you can perform:

[0.5,72, 0.7] |[0.75,200,0.3] |  [0,-18,0.7]
------------ | -------------  | -------------
<img src="Images/example.gif" width="280" height="280">|<img src="Images/example2.gif" width="280" height="280">|<img src="Images/example3.gif" width="280" height="280">

### Server Rules

- If a certain parameter of an action is out of range, the server generates the parameter uniformly at random in the legal range.
- If the coin overlaps with the striker in the initial placement, the server generates a uniformly random free position.
- The server accepts four decimal places of precision. 
- The server also adds a zero mean gaussian noise to the actions of std 0.005 to the position, 2 to the angle, 0.01 to the force.
- If you are Player 2 - on the opposite side of the board, the state you receive is "mirrored" assuming you are playing from Player 1's perspective. You don't have to write separate agents for Player 1 and Player 2.
- The server has a timeout of 0.5 seconds. If any agent takes more time to send an action/sends an empty message, it is disqualified, and the other agent is considered the winner. In the single player case, it ends the game.
-  The ports the agents use to connect to the server can be specified in the parameters. 
- For single player, the server permits a maximum of 500 strikes. If the agent does not manage to clear the board, the game is treated as incomplete.
- For doubles, the server permits a maximum of 200 strikes(by any player). If the board is not cleared, the game ends, and the player with the highest score is the winner. 
- Severs write out experiment results in log files with current time stamps. They can be found in Carrom_rl/logs/ . You can generate the mean statistics using generate_stats.py in the same folder:
- The Server is automatically called using start_experiment.py. 
```
python generate_stats.py <logfile>
```

#### Configuration Parameters

The parameters of the game such as friction, elasticity, dimensions and weights of objects, etc are coded in identical Utils.py for both Servers. Use this file as a reference. These parameters should not be changed, as agents must work using the parameters mentioned in the file.

### Agent parameters

There is one sample agent to get you started. start_agent.py samples the action space uniformly at random. The agent is automatically called using start_experiment.py. 

Parameters passed to the agent are solely disambiguate between 1 player and 2 player games, and to inform the agent whether it is player 1 or 2. A seed is passed to the agent. You must initialize your rng with this seed, to make your results reproducible and consistent across several runs. If in doubt, look at the sample agent provided.

### Experiment Parameters
The experiment is controlled by the parameters passed to start_experiment.py. It calls the server and the agent with appropriate parameters.
```
-np or --num-players [1/2] - 1 Player or 2 Player Carrom [Default: 1]
-ne or --num-experiments [n] - Number of experiments to run. If this is set > 1. the rng passed to the servers and the agents is the current trial number. [Default: 1]
-v or --visualization  [1/0] - Turn visualization on/off [Default: 0]
-p1 or --port1 [n] - The port player 1 agent connects to. Must enter a valid port [Default: 12121]
-p2 or --port1 [n] - The port player 2 agent connects to. Must enter a valid port [Default: 34343]
-rr or --render-rate [1-20] - Render rate, render every x frame. A higher number results in faster visualization, but choppy frames. Only used if -v is set to 1 [Default: 10]
-n or --noise  [1/0] - Turn noise on/off. The final agent will be evaluated with noise. [Default: 1]
-rs or --random-seed [n] - A random seed passed to the server rng [Default: 0]
-a1 or --agent-1-location [file_path] - relative/full path to player 1 agent [Default: carrom_agent/start_agent.py]
-a2 or --agent-2-location [file_path] - relative/full path to player 2 agent [Default: carrom_agent/start_agent.py]
```
At the end of an experiment, a logfile is written summarising the statistics in logs/

## Quick Start

Install main dependences: pygame (1.9.2) and pymunk (5.0)
The code works on python (2.7.12)
```
sudo apt-get install python-pip
sudo pip install pygame
sudo pip install pymunk
```

Fork the repo/download it.

```
git clone https://github.com/samiranrl/Carrom_rl.git
```

Visualize one single player game

```
cd Carrom_rl/
python start_experiment.sh -v 1
```

Simulate 10 single player games

```
cd Carrom_rl/
python start_experiment.sh -ne 10
```

Generate statistics from the previous experiment

```
cd logs/
python generate_stats.py <logfile>
```

Perform the experiment with 2 player Carrom

```
cd Carrom_rl/
python start_experiment.sh -v 1 -np 2
```

You have access to one step noise free ground truth data using: simulate(state,action)->next_state, reward

```
cd Carrom_rl/one_step/
python simulation.py
```

## What to submit?

Please read Readme.txt

You must write a carrom agent, which clears the single player board in <=30 turns on average. generate_stats.py will be called for >=1000 experiments. If the data is invalid, for eg: you have a connection timeout/runtime error/exceed 500 strikes, the statistics will not be counted, so make sure your agent is fully functional (in the sl2 machines) before submission. If confused, open **start_agent.py**, which has helpful built in logic to connect to the carrom server, parse the state and send an action.

### Changes
<b>Version 1.0 - Initial release</b>

Single player server is ready. There might be some issues with the doubles server, they will be fixed later.
The following changes have been made to the server. Please use the latest version of the Server for your assignment.

- fixed fouls in 1p server
- made pockets symmetric
- fixed angle range
- fixed one step simulations
- fixed generate_stats.py
- fixed scoring issue
