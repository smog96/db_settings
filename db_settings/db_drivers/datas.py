from dataclasses import dataclass


@dataclass(frozen=True)
class DbData:
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str
    table_name: str
    service_name: str
