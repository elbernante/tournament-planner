#!/usr/bin/env python
#
# Extra Credit Test cases for tournament.py

from psycopg2 import IntegrityError
from tournament import *
from tournament_test import *

def testPreventRematch():
    deleteMatches()
    deletePlayers()
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]

    reportMatch(id1, id2)
    reportMatch(id3, id4)
    
    try:
        reportMatch(id1, id2)
    except IntegrityError:
        pass
    else:
        raise ValueError("Players should not be able to rematch.")

    try:
        reportMatch(id2, id1)
    except IntegrityError:
        pass
    else:
        raise ValueError("Players should not be able to rematch.")

    try:
        reportMatch(id3, id4)
    except IntegrityError:
        pass
    else:
        raise ValueError("Players should not be able to rematch.")

    try:
        reportMatch(id4, id3)
    except IntegrityError:
        pass
    else:
        raise ValueError("Players should not be able to rematch.")

    print "1. Players can match against each against other only once."

def testOddNumberOfPlayers():
    deleteMatches()
    deletePlayers()
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")
    registerPlayer("Arnold Roddick")
    
    pairings = swissPairings()
    if len(pairings) != 3:
        raise ValueError(
            "For five players, swissPairings should return 3 pairs.")

    p_id = [0] * 6
    bye_count = 0
    [(p_id[0], pname1, p_id[1], pname2), \
        (p_id[2], pname3, p_id[3], pname4), \
        (p_id[4], pname3, p_id[5], pname4)] = pairings

    for pid in p_id:
        if pid == 0:
            bye_count = bye_count + 1

    if bye_count != 1:
        raise ValueError(
            "For odd number of players, one of the players should be assigned a 'BYE'.")

    print "2. If there are odd number of players, one player is assiged a 'BYE'."

def testDrawMatch():
    deleteMatches()
    deletePlayers()
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]

    reportMatch(id1, id2, True) # True = draw match
    reportMatch(id3, id4)

    standings = playerStandings()
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i == id3 and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i == id4 and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
        elif i in (id1, id2) and w != 0:
            raise ValueError("Each player in a draw match should have zero wins recorded.")
    print "3. A match can have a draw."

def testEqualNumberOfWins():
    deleteMatches()
    deletePlayers()
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")

    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]

    # Round 1
    reportMatch(id1, id2)
    reportMatch(id3, id4)

    # Round 2
    reportMatch(id4, id2)   # Loser vs loser
    reportMatch(id1, id3)   # Winner vs Winner

    standings = playerStandings()
    [sid1, sid2, sid3, sid4] = [row[0] for row in standings]

    if sid1 != id1:
        raise ValueError("Player with the most number of wins should be ranked 1st.")
    # id3 and id4 has the same number of wins, but OMW of id3 is 3, and OMW of id2 is 1
    if sid2 != id3:
        raise ValueError("If players have equal number of wins, the player who has more total number of wins of opponents should be ranked higher.")
    if sid3 != id4:
        raise ValueError("If players have equal number of wins, the player who has less total number of wins of opponents should be ranked lower.")
    if sid4 != id2:
        raise ValueError("If players least number of wins should be ranked last.")

    print "4. Players with equal number of wins are ranked according to OMW (Opponent Match Wins)."

def testMultipleTournament():
    deleteTournament()

    # New tournament
    new_t = newTournament("Wimbledon")
    t = getTournaments()
    if len(t) != 2:
        raise ValueError("New tournament should be created.")

    # Delete all tournaments
    deleteTournament()
    t = getTournaments()
    if len(t) != 1:
        raise ValueError("After deleting all tournaments, the default tournament should remain.")

    (t_id, t_title) = t[0]
    if t_id != 0:
         raise ValueError("Default tournament should never able to be deleted.")

    # Multiple tournaments
    new_t1 = newTournament("Wimbledon")
    new_t2 = newTournament("US Open")
    t = getTournaments()
    if len(t) != 3:
        raise ValueError("New tournaments should be created.")

    # Delete 1 tournament
    deleteTournament(new_t1)
    t = getTournaments()
    if len(t) != 2:
        raise ValueError("Only deleted tournamet shoud be removed.")
    (t_d1, t_id2) = [row[0] for row in t]
    if not (0 in [t_d1, t_id2]):
         raise ValueError("Default tournament should never able to be deleted.")
    if not (new_t2 in [t_d1, t_id2]):
         raise ValueError("Only deleted tournamet shoud be removed.")

    # Add players
    p_id1 = addPlayer("Bruno Walton")
    p_id2 = addPlayer("Boots O'Neal")
    p_id3 = addPlayer("Cathy Burton")
    if countPlayers(0) != 0 or countPlayers(new_t2) != 0:
        raise ValueError("There should be no registered players.")

    # Register players
    registerPlayerInTournament(p_id1, 0)
    if countPlayers(0) != 1 or countPlayers(new_t2) != 0:
        raise ValueError("Player should be able to register in tournament.")

    registerPlayerInTournament(p_id1, new_t2)
    if countPlayers(0) != 1 or countPlayers(new_t2) != 1:
        raise ValueError("Player should be able to register in tournament.")

    registerPlayerInTournament(p_id2, new_t2)
    if countPlayers(0) != 1 or countPlayers(new_t2) != 2:
        raise ValueError("Player should be able to register in tournament.")
    
    registerPlayerInTournament(p_id3, 0)
    if countPlayers(0) != 2 or countPlayers(new_t2) != 2:
        raise ValueError("Player should be able to register in tournament.")

    registerPlayerInTournament(p_id3, new_t2)
    if countPlayers(0) != 2 or countPlayers(new_t2) != 3:
        raise ValueError("Player should be able to register in tournament.")

    print "5. Database can support multiple tournaments."


if __name__ == '__main__':
    print "Running regular tests..."
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    print "Success! All tests pass!"
    print "Running extra credit tests.."
    testPreventRematch()
    testOddNumberOfPlayers()
    testDrawMatch()
    testEqualNumberOfWins()
    testMultipleTournament()
    print "Success!  All extra credit tests pass!"