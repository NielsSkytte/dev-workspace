/*
================================================================================
PRE-DEPLOY TEMPLATE  -  <Warehouse_Name>
Run in the target warehouse BEFORE "Update from git" for commits <sha> .. <sha>.
================================================================================

WHAT THIS IS FOR
----------------
Fabric imports each warehouse item independently and does not sequence cross-item
dependencies ("Cross-item dependencies between warehouses and SQL analytics
endpoints aren't currently supported" - Fabric docs, Limitations in source control).

Two consequences need pre-empting. Both are documented in the `fabric-warehouse-git`
skill; this script is the mechanical remedy.

  (1) REMOVING a NOT NULL column.
      DacFx cannot ALTER it away, so it rebuilds the table: shadow table, copy rows
      using the OLD column list, fail on the column that no longer exists.

          Workload Error Code     ObjectNotFoundInCollection
          Workload Error Message  Table '<Table>(1)' columns '<Column>' not found
                                  in etl or database.

      The schema deployment still completes and leaves no orphan, so nothing looks
      wrong - but every affected table comes out EMPTY.

      Dropping the column yourself first is metadata-only and preserves the rows;
      the sync then has nothing to rebuild.

  (2) ADDING a column in one warehouse and CONSUMING it in another, same commit.

          Workload Error Code     DmsImportDatabaseException
          Workload Error Message  Error occured during import database for the
                                  Datawarehouse '...'. File:
                                  <viewschema>/Views/<View>.sql,
                                  Error: Invalid column name '<Column>'.

      Nothing is applied - the import rolls back whole, including the half that
      would have worked.

USAGE
-----
Run the steps in order in the SQL query editor of the TARGET warehouse, once per
environment. Idempotent - safe to re-run, and a no-op where the change already landed.
Step 4 must return all zeros before you run Update from git.

CAVEAT ON STEP 3 - ALTER TABLE ADD can only append, so a pre-added column lands at
the end while the committed DDL may place it mid-table. Only the ordinal differs; it
self-corrects on the next CTAS run, which does SELECT * from the view and so carries
git's intended order.
================================================================================
*/


-- ---------------------------------------------------------------------------
-- STEP 1 - what needs doing in this environment
-- ---------------------------------------------------------------------------
SELECT
     '<Column> columns to drop' = (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '<schema>' AND COLUMN_NAME = '<Column>')
    ,'<DepColumn> missing' = CASE WHEN NOT EXISTS (
        SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA='<schema>' AND TABLE_NAME='<DepTable>'
          AND COLUMN_NAME='<DepColumn>') THEN 1 ELSE 0 END;


-- ---------------------------------------------------------------------------
-- STEP 2 - drop the removed column in place, across every table that has it
--          (guards against failure mode 1)
-- ---------------------------------------------------------------------------
DECLARE @drop varchar(max);

SELECT @drop = STRING_AGG(CAST(
        'ALTER TABLE [' + TABLE_SCHEMA + '].[' + TABLE_NAME + '] DROP COLUMN [<Column>];'
        AS varchar(max)), ' ')
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = '<schema>' AND COLUMN_NAME = '<Column>';

IF @drop IS NOT NULL EXEC (@drop);


-- ---------------------------------------------------------------------------
-- STEP 3 - pre-add every column a DOWNSTREAM warehouse consumes in this commit
--          (guards against failure mode 2). Nullable only - metadata-only change.
-- ---------------------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
               WHERE TABLE_SCHEMA='<schema>' AND TABLE_NAME='<DepTable>'
                 AND COLUMN_NAME='<DepColumn>')
    ALTER TABLE [<schema>].[<DepTable>] ADD [<DepColumn>] varchar(100) NULL;


-- ---------------------------------------------------------------------------
-- STEP 4 - confirm. ALL must be 0 before running Update from git.
-- ---------------------------------------------------------------------------
SELECT
     '<Column> columns remaining' = (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA='<schema>' AND COLUMN_NAME='<Column>')
    ,'views still emitting <Column>' = (
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.VIEWS v
        WHERE v.TABLE_SCHEMA='<viewschema>'
          AND OBJECT_DEFINITION(OBJECT_ID('<viewschema>.'+v.TABLE_NAME)) LIKE '%<Column>%')
    ,'dependency columns missing' = (
        1 - (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
             WHERE TABLE_SCHEMA='<schema>' AND TABLE_NAME='<DepTable>'
               AND COLUMN_NAME IN ('<DepColumn>')));


/*
AFTER Update from git
---------------------
1. Check row counts survived on every table the warning named. If DacFx rebuilt one
   anyway, re-run the transform pipeline for that layer.
2. New objects arrive EMPTY. List them, and decide which need seeding - a table with
   no view that produces it will never be rebuilt by the chain.
3. Re-stamp item identity to the SPN if this environment runs on a schedule - a
   deployment does not carry LastModifiedBy (see the `fabric-deployment` skill).
4. Expect one normalising commit-from-workspace if any view was hand-edited: the
   `-- Auto Generated (Do not modify) <hash>` header will not match and cannot be
   regenerated externally.
*/
