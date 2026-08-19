-- Trigger requirement: maintain a lightweight audit trail when facts are inserted.
CREATE OR REPLACE FUNCTION retail.audit_fact_insert()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO retail.etl_audit(row_id, event_type, details)
    VALUES (NEW.row_id, 'FACT_INSERT', 'Sales fact inserted by ETL/load process');
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_fact_sales_audit ON retail.fact_sales;
CREATE TRIGGER trg_fact_sales_audit
AFTER INSERT ON retail.fact_sales
FOR EACH ROW
EXECUTE FUNCTION retail.audit_fact_insert();
