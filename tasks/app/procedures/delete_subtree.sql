--------------------------------------------
-- Delete a leaf
--------------------------------------------



--------------------------------------------
-- Delete a subtree
--------------------------------------------

DROP FUNCTION IF EXISTS delete_subtree(VARCHAR, INTEGER);
DROP FUNCTION IF EXISTS soft_delete_subtree(VARCHAR, INTEGER);

CREATE FUNCTION delete_subtree(table_name VARCHAR, id INTEGER)
RETURNS VOID
LANGUAGE PLPGSQL AS $$
BEGIN
    EXECUTE format(
        'DELETE FROM %I
        WHERE id IN (
        SELECT descendant FROM %I_relation WHERE ancestor = $1
        )', table_name, table_name
    ) using id;
    EXECUTE format(
        'DELETE FROM %I_relation
        WHERE descendant IN (
        SELECT descendant FROM %I_relation WHERE ancestor = $1
        )', table_name, table_name
    ) using id;
END;
$$;

CREATE FUNCTION soft_delete_subtree(table_name VARCHAR, id INTEGER)
RETURNS VOID
LANGUAGE PLPGSQL AS $$
BEGIN
    EXECUTE format(
        'UPDATE %I
        SET deleted = true
        WHERE id IN (
        SELECT descendant FROM %I_relation WHERE ancestor = $1
        )', table_name, table_name
    ) using id;
END;
$$;
