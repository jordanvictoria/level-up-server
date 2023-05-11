CREATE VIEW GAMES_BY_USER AS
    SELECT
        a.id,
        a.title,
        a.maker,
        a.skill_level,
        a.number_of_players,
        a.creator_id,
        a.type_id,
        u.id user_id,
        u.first_name || ' ' || u.last_name AS full_name
    FROM 
        levelupapi_game a
    JOIN
        levelupapi_gamer g ON a.creator_id = g.user_id
    JOIN
        auth_user u ON g.user_id = u.id


CREATE VIEW EVENTS_BY_USER AS
    SELECT
        a.id,
        a.description,
        a.date,
        a.time,
        a.game_id,
        a.organizer_id,
        u.id user_id,
        u.first_name || ' ' || u.last_name AS full_name
    FROM 
        levelupapi_event a
    JOIN
        levelupapi_gamer g ON a.organizer_id = g.user_id
    JOIN
        auth_user u ON g.user_id = u.id



    