Carrom_rl
=========

An open source Carrom Simulator interface for testing intelligent/learning agents.

[![Join the chat at https://gitter.im/Carrom_rl/Lobby](https://badges.gitter.im/Carrom_rl/Lobby.svg)](https://gitter.im/Carrom_rl/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)


## Introduction

This is the 0.1 release of Carrom_rl - A Carrom two player Simulator, which provides an interface that allows you to design agents that connect to single player and doubles carrom servers, to play. It is built in python, using pygame + pymunk. This is the course project for [CS 747 - Foundations of Intelligent and Learning Agents](https://www.cse.iitb.ac.in/~shivaram/teaching/cs747-a2016/index.html), taught by [Prof. Shivaram Kalyanakrishnan](https://www.cse.iitb.ac.in/~shivaram/) at IIT Bombay.

Feedback/suggestions/bugs are welcome.

## Carrom

![Carrom Board](https://i.ytimg.com/vi/LvryHWCgK0s/maxresdefault.jpg)
Image Source: https://i.ytimg.com/vi/LvryHWCgK0s/maxresdefault.jpg

The objective of the game is to use a striker disk with a flick of the finger to sink the lighter called carrom men/coins, into one of the corner pockets. A carrom set contains 19 coins in three distinct colours: white and black corresponding to each player and red for the queen.
The aim of the game is to pocket one's own nine coins and the queen before your opponent. (The first player may only pocket white)

The full description, and list of rules and regulations can be found at http://www.carrom.org/


### Why Carrom? 

It is a challenging domain:

- The state space  is continious
- The action space is continious, with added noise
- The agent must adhere to the rules of carrom
- In the two player case, the agent must plan a strategy against an adversary, making it a multi agent system

## Rules
We slightly modify the rules of the game.

### Single Player Server

<img src="Images/p1.gif" width="300" height="300">

The goal of single player carrom is to design an agent, that clears the board as fast as possible, adhering to the following rules:

- Both the white and black coins are treated as the player's. Each coin pocketed increase your score by 1.
- The queen must be pocketed before the last coin.
- If all the coins are pocketed except the queen, one of the coins is taken out of the pocket and put in the center.
- After pocketing the queen, you must sink one of your pieces, thereby 'covering' it, into any pocket in the next shot, or she is returned to the center spot.
- If you pocket the queen along with another of your own piece, it is covered by default.
- A covered queen will increase your score by three points
- If the striker goes into the hole, it counts as a foul. All the pocketed coins in that turn are placed in the center. The score does not increase.

The simulation displays the current score of the player, and the time elapsed since the server was initialized.

### Doubles Server

<img src="Images/p2.gif" width="300" height="300">

The goal of doubles is to design an agent, that wins against an opponent in a game of carrom(by pocketing his coins first), adhering to the following rules:

- The player to start/break must target white coins only. The other player must target black. Players' score increase by one when they pocket their own coin. You get to strike in alterate turn unless you pocket the queen(see below)
- If the player pockets his opponent's coin, it counts as a foul. All coins pocketed that turn are kept in the center, and the score does not increase.
- If all the coins are pocketed except the queen, the other player wins the match.
- If you manage to pocket all of your own coins, and the opponent pockets and covers the queen, you win the match.
- After pocketing the queen, you must sink one of your pieces, thereby 'covering' it, into any pocket in the next shot, or she is returned to the center spot.
- If you pocket the queen along with another of your own piece, it is covered by default.
- A covered queen will increase your score by three points
- If the striker goes into the hole, it counts as a foul. All the pocketed coins in that turn are placed in the center. The score does not increase.

The simulation displays the current score of player 1 and player 2, and the time elapsed since the server was initialized.

## The agent and the environment


### State

We formally define the carrom environment in the reinforcement learning context. The State is a list of current coin positions (x,y) coordinates returned to the user, and the current score of the player. If a coin is not present, it is assumed to be pocketed in one of the previous strikes. The state also includes the current score of the player. An example of the state is:

'"State={'White_Locations': [(400,368),(437,420), (372,428),(337,367), (402,332), (463,367), (470,437), (405,474), (340,443)], 'Red_Location': [(400, 403)], 'Score': 0, 'Black_Locations': [(433,385),(405,437), (365,390), (370,350), (432,350), (467,402), (437,455), (370,465), (335,406)]}"'

It is returned in the form of a string to the agent, which must be parsed. The logic for parsing such a state is built in the sample agent for your reference. 

### Action

The action is a three dimentional vector: [angle,position,force]

- angle : The angle gives the direction (in radians), where you want to strike the striker. Accepts floats in the range [0-3.925] and 5.495 to 6.28. 
- position: The legally valid x position of the striker on the board. Accepts floats between [0-1] (normalized). 0 is the extreme left position, and 1 is the exteme right. 

[](http://www.carrom.org/pix/wrong.gif)

(When placing the striker on the board to shoot, the striker must touch both 'base lines' (see left diagram), either covering the red circle completely, or not touching it at all. The striker may not touch the diagonal arrow line.)

Source: http://www.carrom.org/game/?subcat=11

- force: The force with with you want to hit the striker. Accepts floats between [0-1] (normalized). The maximimum force makes the striker cover a distance of 3.5 times the width of the board, starting from the center, striking the walls 4 times, and touching nothing else. There is a minimum force with which you strike (even if you pass 0)

For example, you want to play a shot from the centre of the board, with and angle of approximately 72 degrees and 70% of the maximum force.
You will pass the action [0.8 * 3.14/2, 0.5, 0.7]. It will look like this:

<img src="Images/example.gif" width="300" height="300">


### Server

- If an illegal parameter is passed to the server, it generates it at random, uniformly within the range
- The server accepts four decimal places of precision. 
- The server also adds a zero mean gaussian noise to the actions.
- If you are Player 2 - on the opposite side of the board, the state you recieve is "mirrored" assuming you are playing from player 1's perspective. You don't have to write separate agents for Player 1 and Player 2.
- The server has a timeout of 0.5 seconds. If any agent does takes more time to send an action, the other agent is considered as the winner. In the single player case, it ends the game.
- When a game finished, a log file is written in the format:

### Sample Agents


## Quick Start

Install main dependences: pygame (1.9.2) and pymunk (5.0)
```
sudo apt-get install python-pip
sudo pip install pygame
sudo pip install pymunk
```

Fork the repo/download it.
```
git clone https://github.com/samiranrl/Carrom_rl.git
```

Start the one player server. Server and agent must be launched from separate terminals.
```
cd Carrom_rl/Carrom_1Player/
python ServerP1.py -p 12121 -v 1
python Agent_random.py -p 12121
```
Start the doubles server. Server and agents must be launched from separate terminals.
```
cd Carrom_rl/Carrom_2Player/
python ServerP1.py -p1 12121 -p2 34343 -v 1
python Agent_random.py -p 12121
python Agent_improved.py -p 34343
```



## What to submit?

Python is preferred. 




## To Do

- Fix Theta 
- Handle exceptions on closing the connection
- Add replayer
- Test if scores are updated properly
- Refactoring and cleaning up code
- SL-2 Machines
- Add visualization speedup parameter(with ranges)


## License

[![GNU GPL v3.0](http://www.gnu.org/graphics/gplv3-127x51.png)](http://www.gnu.org/licenses/gpl.html)
