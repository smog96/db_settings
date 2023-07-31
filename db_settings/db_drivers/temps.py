from string import Template

postgres_connection_string = Template(
    "dbname=${name} user=${user} password=${password} host=${host} port=${port}"
)
