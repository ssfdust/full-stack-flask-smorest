----------------
-- Get child nodes
----------------

DROP FUNCTION IF EXISTS get_child_nodes(VARCHAR, INTEGER);

DROP TYPE IF EXISTS tree_type CASCADE;

CREATE TYPE tree_type AS (id int,deleted BOOLEAN,pid int,name text,depth INTEGER,breadcrumbs text);

-- Create function
CREATE OR REPLACE FUNCTION get_child_nodes(VARCHAR, INTEGER)
  RETURNS SETOF tree_type
LANGUAGE PLPGSQL AS $$
BEGIN
RETURN QUERY EXECUTE format(
$q$ SELECT d.id,
       d.deleted, d.pid,
       concat(repeat('——', p.distance), d.name) AS tree,
       p.distance,
       array_to_string(array_agg(crumbs.ancestor::CHARACTER VARYING ORDER BY crumbs.ancestor),',','*') breadcrumbs
  FROM %I AS d
  JOIN %I_relation AS p ON d.id = p.descendant
  JOIN %I_relation AS crumbs ON crumbs.descendant = p.descendant
 WHERE p.ancestor = $1 AND d.deleted = false
 GROUP BY d.id, p.distance
 ORDER BY d.id ASC $q$, $1, $1, $1
) using $2;
END;
$$;

