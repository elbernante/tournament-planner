Tournament Planner
==================

Swiss system for pairing up players in each round in game tournament.


Setting Up
--------------------------------------

### Environment Requirements

The following needs to be installed:

- Python 2.7
- PostgreSQL 9.3
- Git

### Getting the Source Code

Clone a copy of the main Movie Index git repo by running:

```bash
git clone https://github.com/elbernante/tournament-planner.git
```

### Setting up the database

This app is using a PostgreSQL database named ***'tournament'***. Make sure you don't have any other database of the same name already exists in your system.

In the command line, go to the directory of ```tournament-planner/``` where you cloned the repo and run the command:

```bash
psql
```

It should put you in PostgreSQL command. Then import the ```tournament.sql``` file by running the command:

```bash
\i tournament.sql
```

After running the script, a database named ***'tournament'*** should be created with all the necessary tables and views. To exit from PostgreSQL command, enter command ```\q```.


### Running the Tests

After setting up the database, in the command line, go to the directory of ```tournament-planner/``` and run the command:

```bash
python tournament_test.py
```

### Running the Extra Credit Tests

After setting up the database, in the command line, go to the directory of ```tournament-planner/``` and run the command:

```bash
python extra_credit_test.py
```

