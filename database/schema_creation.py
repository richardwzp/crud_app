import sqlite3
from enum import Enum
from typing import Optional, List

from database import create_database_instance

tables = [
    """
CREATE TABLE inventory (
    cost VARCHAR(20) NOT NULL,
    country_code_of_origin CHAR(2) NOT NULL,
    create_at VARCHAR(30) NOT NULL,
    harmonized_system_code VARCHAR(20) NOT NULL,
    id INT NOT NULL PRIMARY KEY,
    province_code_of_origin CHAR(2) NOT NULL,
    sku varchar(20) NOT NULL,
    tracked INT NOT NULL,
    updated_at VARCHAR(30) NOT NULL,
    required_shipping INT NOT NULL 
)
""",
    """
CREATE TABLE country_harmonized_system_codes (
    harmonized_system_code VARCHAR(20) NOT NULL,
    country_code CHAR(2),
    inventory_id INT,
    CONSTRAINT harmonize_primary PRIMARY KEY (harmonized_system_code, country_code, inventory_id),
    CONSTRAINT relate_to_inventory FOREIGN KEY(inventory_id) REFERENCES inventory(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE 
)
"""
]


def create_all_tables(inst: sqlite3.Connection):
    new_cur = inst.cursor()
    for table in tables:
        new_cur.execute(table)
    inst.commit()

if __name__ == '__main__':
    with create_database_instance() as instance:
        create_all_tables(instance)
