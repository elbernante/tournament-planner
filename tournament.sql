-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- NOTE: This assumes a database named 'tournament' does NOT already exist.
--			If 'tournament' database already exists, comment out the
--			`CREATE DATABASE tournament` statement,
--			uncomment the DROP statements for views, trigger, and table.

-- Create tournament database
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;

-- Connect to tournament database
\c tournament;

/**
  * Drop existing tables, triggers, and view if they already exists
  */
-- Drop views first, in this order:
-- DROP VIEW IF EXISTS swiss_pair;
-- DROP VIEW IF EXISTS player_standing;
-- DROP VIEW IF EXISTS opponent_list;
-- DROP VIEW IF EXISTS win_count;

-- Drop triggers
-- DROP TRIGGER IF EXISTS new_tournament ON tournament;

-- Drop tables in this order:
-- DROP TABLE IF EXISTS match;
-- DROP TABLE IF EXISTS registry;
-- DROP TABLE IF EXISTS player;
-- DROP TABLE IF EXISTS tournament;


-- Helper function to sort array
CREATE OR REPLACE FUNCTION sort_array(int[]) RETURNS int[] AS $$
    SELECT array_agg(n) FROM (SELECT n FROM unnest($1) AS t(n) ORDER BY n) AS a;
$$ LANGUAGE sql IMMUTABLE;


/**
  * tournament table
  * List of available tournament.
  *		More than one tournament is supported.
  */
CREATE TABLE tournament (
	id 		serial PRIMARY KEY NOT NULL,
	title 	varchar(40)
);


/**
  * player table
  * List of players
  */
CREATE TABLE player (
	id 		serial PRIMARY KEY NOT NULL,
	name	varchar(80)
);


/**
  * registry table
  * List of players registered to a tournament.
  * 	A player can register to several tournaments,
  *		once per tournament.
  */
CREATE TABLE registry (
	tournament_id 	int NOT NULL REFERENCES tournament (id),
	player_id 		int NOT NULL REFERENCES player (id),
	PRIMARY KEY (tournament_id, player_id)
);


/**
  * match table
  * List of matches between players per tournament
  * Rematches between players are prevented.
  */
CREATE TABLE match (
	tournament_id 	int NOT NULL,
	player_id_1 	int NOT NULL,
	player_id_2 	int NOT NULL,
	winner			int NOT NULL,
	PRIMARY KEY (tournament_id, player_id_1, player_id_2),
	CONSTRAINT self_match CHECK (player_id_1 <> player_id_2),	-- Prevent player from matching against itself
	CONSTRAINT valid_winner 									-- Allow only valid winner:
		CHECK (
			((winner = -1) 										-- 		Match can be a draw (-1)
				OR (winner = player_id_1) 						-- 		Winner can be either of the player
				OR (winner = player_id_2))
			AND winner <> 0),									-- 		A BYE player (0) cannot be a winner
	CONSTRAINT registered_player_1 								-- A match can only be played between
		FOREIGN KEY (tournament_id, player_id_1) 				--		players who are registered
		REFERENCES registry (tournament_id, player_id),			--		in the tournament
	CONSTRAINT registered_player_2
		FOREIGN KEY (tournament_id, player_id_2)
		REFERENCES registry (tournament_id, player_id)
);


/**
  * Prevent rematches between players per tournament
  * 	match(player2, player1) is not allowed if
  *		match(player1, player2) already exists
  */
CREATE UNIQUE INDEX unique_match
	ON match (tournament_id, sort_array(array[player_id_1, player_id_2]));


/**
  * Create BYE player. Use as trigger for INSERT in tournament table.
  */
CREATE OR REPLACE FUNCTION generate_bye_player() RETURNS TRIGGER
AS $generate_bye_player$
	BEGIN

		-- Create BYE player
		IF NOT EXISTS (SELECT id FROM player WHERE id = 0)
		THEN
			INSERT INTO player (id, name) VALUES (0, 'BYE');
		END IF;

		-- Register BYE player to the new tournament
		IF NOT EXISTS (SELECT tournament_id FROM registry
			WHERE tournament_id = NEW.id AND player_id = 0)
		THEN
			INSERT INTO registry (tournament_id, player_id) VALUES (NEW.id, 0);
		END IF;

		RETURN NULL;
	END;
$generate_bye_player$ LANGUAGE plpgsql;


-- Automatically create BYE player for every new tournament
CREATE TRIGGER new_tournament AFTER INSERT ON tournament
	FOR EACH ROW
	EXECUTE PROCEDURE generate_bye_player();


/**
  * Number of wins per player per tournament
  */
CREATE VIEW win_count AS
	SELECT
		registry.tournament_id,
		registry.player_id,
		count(match.winner) AS wins
	FROM
		registry
		LEFT OUTER JOIN match
			ON 	registry.tournament_id = match.tournament_id
				AND registry.player_id = match.winner
	GROUP BY
		registry.tournament_id,
		registry.player_id
	ORDER BY
		registry.tournament_id ASC,
		registry.player_id ASC;


/**
  * List of opponents per player per tournament
  */
CREATE VIEW opponent_list AS
	SELECT
		op_list.tournament_id as tournament_id,
		op_list.player_id as player_id,
		op_list.opponent_id as opponent_id,
		win_count.wins as opponent_wins
	FROM
		(
			SELECT
				registry.tournament_id as tournament_id,
				registry.player_id as player_id,
				(CASE WHEN registry.player_id = match.player_id_1
					THEN match.player_id_2
					ELSE match.player_id_1 END) as opponent_id
			FROM
				registry
				JOIN match
					ON 	registry.tournament_id = match.tournament_id
						AND (
								registry.player_id = match.player_id_1
								OR registry.player_id = match.player_id_2
							)
			ORDER BY
				registry.tournament_id ASC,
				registry.player_id ASC
		) AS op_list
		JOIN win_count
			ON 	op_list.tournament_id = win_count.tournament_id
				AND op_list.opponent_id = win_count.player_id
		ORDER BY
			op_list.tournament_id,
			op_list.player_id;


/**
  * Player Standings
  * Players are ranked base on their number of wins.
  * 	If 2 players have the same number of wins,
  *		the are ranked according to OMW (Opponent Match Wins)
  */
CREATE VIEW player_standing AS
	SELECT
		Row_Number() OVER (PARTITION BY standing.tournament_id) as rank,
		standing.*
	FROM
		(
			SELECT
				win_count.tournament_id AS tournament_id,
				win_count.player_id AS player_id,
				player.name as name,
				win_count.wins AS wins,
				count(opponent_list.opponent_id) AS matches,
				sum(opponent_list.opponent_wins) AS opponent_wins	-- Combined total number of wins of the player's opponents
			FROM
				win_count
				LEFT OUTER JOIN opponent_list
					ON 	win_count.tournament_id = opponent_list.tournament_id
						AND win_count.player_id = opponent_list.player_id
				LEFT OUTER JOIN player
					ON win_count.player_id = player.id
			WHERE
				win_count.player_id <> 0
			GROUP BY
				win_count.tournament_id,
				win_count.player_id,
				player.name,
				win_count.wins
			ORDER BY
				win_count.tournament_id ASC,
				win_count.wins DESC, 			-- Rank by number of wins
				opponent_wins DESC NULLS LAST,  -- Then by combined total number of wins of thier opponents
				matches DESC,
				win_count.player_id ASC
		) AS standing;


/**
  * Swiss Pairing
  * If there is an odd number players
  * 	one player is paired to a "BYE"
  */
CREATE VIEW swiss_pair AS
	SELECT
		ps1.tournament_id,
		ps1.player_id as player_id_1,
		ps1.name as player_name_1,
		(CASE WHEN ps2.player_id IS NULL
			THEN 0 ELSE ps2.player_id END) as player_id_2, -- Pair the odd player with BYE
		(CASE WHEN ps2.name IS NULL
			THEN 'BYE' ELSE ps2.name END) as player_name_2
	FROM
		player_standing as ps1
		LEFT OUTER JOIN player_standing as ps2
			ON 	ps1.tournament_id = ps2.tournament_id
				AND ps1.rank = ps2.rank - 1
	WHERE
		ps1.rank % 2 = 1;


-- Create Default Tournament
INSERT INTO tournament (id, title) VALUES (0, 'Default Tournament');

