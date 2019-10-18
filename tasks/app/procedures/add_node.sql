DROP FUNCTION IF EXISTS insert_node(CHARACTER VARYING,INTEGER,INTEGER);
CREATE OR REPLACE FUNCTION insert_node(table_name varchar, id int, pid int) RETURNS void LANGUAGE PLPGSQL AS $$
BEGIN
    IF pid IS NULL THEN
        pid = id;
    END IF;
    EXECUTE format(
        'INSERT INTO %I_relation(ancestor, descendant, distance)
        SELECT ancestor, $1 as descendant, distance + 1
        FROM %I_relation WHERE descendant = $2
        UNION ALL SELECT $3, $4, 0',
        table_name, table_name
    ) using id, pid, id, id;
END;
$$;
