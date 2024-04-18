CREATE OR REPLACE PROCEDURE increment_counter(
    INOUT counter INT -- used as both the input and output
)
LANGUAGE PLPGSQL
AS $$
BEGIN
    counter := counter + 1; 
END;
$$;

-- calling it
CALL increment_counter(?);