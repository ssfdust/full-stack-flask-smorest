DROP FUNCTION IF EXISTS move_subtree(VARCHAR, Integer, Integer);

CREATE OR REPLACE FUNCTION move_subtree(
  table_name VARCHAR,
  id Integer,
  pid Integer
)
RETURNS VOID
LANGUAGE PLPGSQL AS $$
BEGIN
    --------------------------------------------
    -- Step 1: Update parent node id
    --------------------------------------------
    EXECUTE format('UPDATE %I SET pid = $2 WHERE id = $1', table_name)
    using id, pid;

    --------------------------------------------
    -- Step 2: Disconnect from current ancestors
    -- Delete all paths that end at descendants in the subtree
    --------------------------------------------
    EXECUTE format('DELETE FROM %I_relation
    WHERE descendant IN (SELECT descendant FROM %I_relation WHERE ancestor = $1)
    AND ancestor IN (SELECT ancestor FROM %I_relation
        WHERE descendant = $1 AND ancestor != descendant)', table_name, table_name, table_name)
        using $2;

    --------------------------------------------
    -- Step 2: Mount subtree to new ancestors
    -- Insert rows matching ancestors of insertion point and descendants of subtree
    --------------------------------------------
    IF $3 IS NOT NULL THEN
        EXECUTE format('INSERT INTO %I_relation (ancestor, descendant, distance)
        SELECT supertree.ancestor, subtree.descendant, supertree.distance + subtree.distance + 1
        FROM %I_relation AS supertree
        CROSS JOIN %I_relation AS subtree
        WHERE supertree.descendant= $2
        AND subtree.ancestor= $1', table_name, table_name, table_name)
        using $2, $3;
    END IF;
END;
$$;
