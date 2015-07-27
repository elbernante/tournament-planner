#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#
'''
Tournament Planner: Full Stack Nano Degree Project 2
'''

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches(tournament_id=-1):
    """Remove all the match records from the database.

    Args:
      tournament_id:    Optional. The ID of the tournament from where to delete all matches.
                        If tournament_id = -1, it deletes all matches in all tournaments.
                        Default: -1.
    """

    query = "DELETE FROM match WHERE tournament_id = %s;"

    if tournament_id == -1:
        query = "DELETE FROM match;"

    conn = connect()
    cur = conn.cursor()
    cur.execute(query, (tournament_id,))
    conn.commit()

    cur.close()
    conn.close()


def deletePlayers(tournament_id=-1):
    """Remove all the player records from the database.

    Args:
      tournament_id:    Optional. The ID of the tournament from where to delete the players.
                        If tournament_id = -1, it deletes all the players in all tournaments.
                        Default: -1.
    """

    deleteMatches(tournament_id) # Matches should be deleted first before players can be deleted

    conn = connect()
    cur = conn.cursor()

    if tournament_id == -1:
        registry_query = "DELETE FROM registry;"
        player_query = "DELETE FROM player;"
        cur.execute(registry_query)
        cur.execute(player_query)
    else:
        registry_query = "DELETE FROM registry WHERE tournament_id = %s;"
        cur.execute(registry_query)

    conn.commit()

    cur.close()
    conn.close()

def countPlayers(tournament_id=0):
    """Returns the number of players currently registered.

    Args:
      tournament_id:    Optional. The ID of the tournament to count the number of registered player.
                        Default: 0.
    """

    query = "SELECT count(*) FROM registry WHERE tournament_id = %s AND player_id <> 0 GROUP BY tournament_id;"

    conn = connect()
    cur = conn.cursor()

    cur.execute(query, (tournament_id,))
    result = cur.fetchone()
    count = result[0] if result else 0

    cur.close()
    conn.close()

    return count

def addPlayer(name):
    """Adds a player to the tournament databaase and returns the id.
    The added player is not yet registered to any tournament.
    """

    query = "INSERT INTO player (name) VALUES (%s) RETURNING id;"

    conn = connect()
    cur = conn.cursor()

    cur.execute(query, (name,))
    conn.commit()

    player_id = cur.fetchone()[0]

    cur.close()
    conn.close()

    return player_id

def registerPlayerInTournament(player_id, tournament_id=0):
    """Registers a player to a tournament.

    Args:
      player_id:        ID of the player to be registered. The ID must be valid value returned from addPlayer().
      tournament_id:    Optional. The id of the tournament to where to register the player.
                        Default: 0.
    """

    query = "INSERT INTO registry (tournament_id, player_id) VALUES (%s, %s);"

    conn = connect()
    cur = conn.cursor()

    cur.execute(query, (tournament_id, player_id))
    conn.commit()

    cur.close()
    conn.close()

def registerPlayer(name, tournament_id=0):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
      tournament_id:    Optional. The id of the tournament to where to register the player.
                        Default: 0.
    """

    registerPlayerInTournament(addPlayer(name), tournament_id)

def playerStandings(tournament_id=0):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Args:
      tournament_id:    Optional. The ID of the tournament from where to retrieve player standings.
                        Default: 0.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    query = "SELECT player_id, name, wins, matches FROM player_standing WHERE tournament_id = %s;"

    conn = connect()
    cur = conn.cursor()

    cur.execute(query, (tournament_id,))
    result = cur.fetchall()

    cur.close()
    conn.close()

    return result


def reportMatch(winner, loser, isDraw=False, tournament_id=0):
    """Records the outcome of a single match between two players.

    Args:
      winner:           the id number of the player who won
      loser:            the id number of the player who lost
      isDraw:           the match is draw
      tournament_id:    Optional. The ID of the tournament to where to report the match.
                        Default: 0.
    """

    query = "INSERT INTO match (tournament_id, player_id_1, player_id_2, winner) VALUES (%s, %s, %s, %s);"

    conn = connect()
    cur = conn.cursor()

    cur.execute(query, (tournament_id, winner, loser, -1 if isDraw else winner))
    conn.commit()

    cur.close()
    conn.close()

def swissPairings(tournament_id=0):
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Args:
      tournament_id:    Optional. The ID of the tournament from where to retrieve pairings.
                        Default: 0.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    query = "SELECT player_id_1, player_name_1, player_id_2, player_name_2 FROM swiss_pair WHERE tournament_id = %s;"

    conn = connect()
    cur = conn.cursor()

    cur.execute(query, (tournament_id,))
    result = cur.fetchall()

    cur.close()
    conn.close()

    return result


