Assignment 4, CS747, Autumn 2016



In this assignment, you must implement an agent to play the game of Carrom. The agent must demonstrate the proficiency to clear the board in fewer than 30 moves.





CARROM SIMULATOR



Your first order of business is to get familiar with a Carrom simulator that your TAs have developed. Code and documentation are available at the following site.



  https://github.com/samiranrl/Carrom_rl





TEAMS



Unike previous assignments, you will work on this assignment in teams. Talk to your classmates and make teams of 3 (in exceptional cases, 2 or 1). You are welcome to use the class Moodle page to send out an interest and find partners.



You need to register your team with the TAs. From each team, one member must send e-mail to samiranroy@cse.iitb.ac.in, siddarth@cse.iitb.ac.in, and ashishr@cse.iitb.ac.in, with all the team members CC-ed. Provide a team name, which will also be the name of the directory you eventually submit (no special characters) 



Your team needs to be registered by midnight Thursday, October 20.



You will carry over the same teams to your final project.





SUBMISSION



Each team must make exactly one submission through Moodle (that is, one team member must submit).



Suppose your team is called TeamName. You must submit a directory called TeamName, which contains all the source and executable files of your agent. The directory must contain a script titled start_agent.py, which must take in command line arguments in the same format as the identically-named script provided in the code. You are free to build upon the sample python agent provided, or otherwise to implement an agent in any programming language of your choice.



Your code will be tested by running an experiment that calls start_agent.py in your directory: before you submit, make sure you can successfully run start_experiment.py on the departmental machines (sl2-*.cse.iitb.ac.in), wherein YOUR SCRIPT start_agent.py is called in single-agent mode.



Include a file called notes.txt in your TeamName directory, which (1) describes the algorithm your agent implements, and (2) provides references to any libraries and code snippets you have utilised.



In summary: you must submit your TeamName directory (compressed as TeamName.tar.gz) through Moodle. The directory must contain start_agent.py, along with all the sources and executables for the agent, as well as a notes.txt file.





EVALUATION



Your agent will be tested by running a large number of experiments (at least 1000), each time with a separate random seed. Each run will terminate after the agent clears the board, or after 200 strikes, whichever is earlier. The average number of strikes per game for your agent will be calculated based on the runs. If this number is below 30, your agent passes the evaluation; otherwise it fails.



The instructor may look at your source code and notes to corroborate the results obtained by your agent, and may also call you to a face-to-face session to explain your code.





DEADLINE AND RULES



Your submission is due by 11.55 p.m., Tuesday, October 25.  You will get a score of zero if your code is not received by the deadline. (Recall that the deadline for registering your team--by sending the TAs e-mail--is midnight, Thursday, October 20.)



Your team must work alone on this assignment. Do not share any code (whether yours or code you have found on the Internet) with other teams. Do not discuss the design of your agent with anybody outside your team.



You will not be allowed to alter your code in any way after the submission deadline. Before submission, make sure that it runs on the sl2 machines.





FEEDBACK



The TAs have coded up the simulator in the short span of a few weeks, and in spite of their best efforts, it is entirely possible that there are inconsistencies and bugs in the code. Do help this project by bringing up any such issues either on the relevant Github page:



    https://github.com/samiranrl/Carrom_rl/issues.



If you report a bug, provide the steps to reproduce the bug. The instructor and TAs will do their best to resolve issues (which might necessitate updates to the code) in a reasonable way, and appreciate your cooperation.





USE OF CODE FOR RESEARCH PURPOSES



Your instructor and TAs would like to use your submissions to this programming assignment and to your final project for the purposes of research. Specifically, they intend to build a library of agents for playing carrom, and extract measurements when these agents play in single-agent mode, and against each other. Agents will be kept anonymous.



By default, the instructor assumes that you allow the addition of your agent into the library. If, however, you do not wish for your agent to be included, let the instructor and TAs know by sending them e-mail.
