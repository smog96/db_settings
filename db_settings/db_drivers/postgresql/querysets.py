from string import Template

CHECK_TABLE = Template("""SELECT count(*) FROM ${table_name};""")

CREATE_TABLE = Template(
    """CREATE TABLE IF NOT EXISTS ${table_name} (
    id serial PRIMARY KEY,
    service_name varchar(45) NOT NULL,
    val_key varchar(45) NOT NULL,
    value varchar(450) NOT NULL,
    UNIQUE (service_name, val_key)
);"""
)

INSERT_OR_UPDATE = Template(
    """INSERT INTO ${table_name} (service_name, val_key, value)
    VALUES('${service_name}', '${key}', '${value}') 
    ON CONFLICT (service_name, val_key)
    DO UPDATE 
    SET value = '${value}' 
        WHERE ${table_name}.val_key = '${key}' 
        AND ${table_name}.service_name = '${service_name}';"""
)

SELECT_ONE = Template(
    """SELECT value 
    FROM ${table_name} 
    WHERE val_key = '${key}' 
    AND service_name = '${service_name}';"""
)

SELECT_ALL = Template(
    """SELECT val_key as key, value 
    FROM ${table_name} 
    WHERE service_name = '${service_name}';"""
)

RECOVERY_STATE = Template("""select pg_is_in_recovery();""")
DEFAULT_TRANSACTION_RO = Template("""show default_transaction_read_only;""")
