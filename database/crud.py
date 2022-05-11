import copy
import datetime
import functools
import sqlite3
from typing import Dict, List
from functools import wraps

from database import create_database_instance


def bool_to_int(bo: bool):
    return 1 if bo else 0


def integrity_check(func):
    functools.wraps(func)

    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except sqlite3.IntegrityError as e:
            print(str(e))
            return False
        return True

    return wrapper


@integrity_check
def insert_inventory(inst: sqlite3.Connection,
                     *,
                     cost,
                     country_code_of_origin,
                     harmonized_system_code,
                     id,
                     province_code_of_origin,
                     sku,
                     tracked,
                     required_shipping,
                     country_harmonized_system_codes):
    cur = inst.cursor()
    # create the inventory
    current_time = datetime.datetime.now().isoformat()
    cur.execute("INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [str(float(cost)),
                 country_code_of_origin,
                 current_time,
                 harmonized_system_code,
                 int(id),
                 province_code_of_origin,
                 sku,
                 tracked,
                 current_time,  # inventory["updated_at"],
                 required_shipping])

    # create the country harmonized code
    inventory_id = id
    har_codes = country_harmonized_system_codes
    for har in har_codes:
        h_code, country_code = har["harmonized_system_code"], har["country_code"]
        cur.execute("INSERT INTO country_harmonized_system_codes VALUES(?, ?, ?)",
                    (h_code, country_code, inventory_id))
    cur.close()
    inst.commit()


def delete_inventory(inst: sqlite3.Connection, inventory_id):
    curr = inst.cursor()
    curr.execute("SELECT * FROM inventory WHERE id= ? ", [inventory_id])
    if len(curr.fetchall()) == 0:
        curr.close()
        print(f"trying to delete inventory id {inventory_id} that does not exist")
        return False
    curr.close()

    curr = inst.cursor()
    try:
        curr.execute("DELETE FROM inventory WHERE id= ? ", [inventory_id])
        curr.close()
        inst.commit()
        return True
    except Exception as e:
        print(str(e))
        curr.close()
        return False


def edit_inventory(inst: sqlite3.Connection, inventory_id, edit_items: Dict):
    chsc = None if "country_harmonized_system_codes" \
                   not in edit_items else edit_items["country_harmonized_system_codes"]
    if "country_harmonized_system_codes" in edit_items:
        del edit_items["country_harmonized_system_codes"]

    if "country_harmonized_system_codes" in edit_items:
        del edit_items["country_harmonized_system_codes"]
    sttm = "UPDATE inventory " + \
           "SET " + \
           ", ".join([f"{key} = ?" for key, value in edit_items.items()]) + \
           " WHERE " + \
           f"id={inventory_id}"

    delete_current_codes = "DELETE FROM country_harmonized_system_codes WHERE inventory_id = ?"
    insert_new_code = "INSERT INTO country_harmonized_system_codes VALUES(?, ?, ?)"
    cur = inst.cursor()
    try:
        cur.execute(sttm, [value for _, value in edit_items.items()])
        if chsc is not None:
            # first delete all existing ones
            cur.execute(delete_current_codes, (inventory_id,))
            for har in chsc:
                h_code, country_code = har["harmonized_system_code"], har["country_code"]
                cur.execute(insert_new_code, (h_code, country_code, inventory_id))
        cur.close()
        inst.commit()
        return True
    except Exception as e:
        print(str(e))
        cur.close()
        return False


def get_inventory(inst: sqlite3.Connection, ids: List):
    sttm = f"SELECT * FROM inventory WHERE id IN ({', '.join(('?' for _ in ids))})"
    curr = inst.cursor()
    curr.execute(sttm, ids)
    results = curr.fetchall()
    curr.close()
    inventories = []
    keys = ["cost",
            "country_code_of_origin",
            "create_at",
            "harmonized_system_code",
            "id",
            "province_code_of_origin",
            "sku",
            "tracked",
            "updated_at",
            "required_shipping"]
    for result in results:
        iter_inventory = iter(result)
        inventory_json = {}
        inventories.append(inventory_json)
        for key in keys:
            inventory_json[key] = next(iter_inventory)
        chcs_li = []
        inventory_json["country_harmonized_system_codes"] = chcs_li
        # now fetch the harmonized country code
        sttm = f"SELECT * FROM country_harmonized_system_codes " \
               f"WHERE country_harmonized_system_codes.inventory_id = ?"
        curr = inst.cursor()
        curr.execute(sttm, [inventory_json["id"]])
        cresult = curr.fetchall()
        for result in cresult:
            chcs_li.append({"harmonized_system_code": result[0],
                            "country_code": result[1]})
        curr.close()

    return {"inventory_items": inventories}


if __name__ == '__main__':
    conn = create_database_instance()
    # delete_inventory(conn, 1532646)
    insert_inventory(conn,
                     **{"cost": 20,
                        "country_code_of_origin": "FR",
                        "harmonized_system_code": "123456",
                        "id": "1532222",
                        "province_code_of_origin": "CA",
                        "sku": "huh123",
                        "tracked": True,
                        "required_shipping": False,
                        "country_harmonized_system_codes":
                            [{"harmonized_system_code": "123456",
                              "country_code": "CA"}]})
    print(get_inventory(conn, [1532222, 1530000]))
    # edit_inventory(conn, 1532646, {"country_code_of_origin": "FF",
    #                                "country_harmonized_system_codes": [
    #                                    {"harmonized_system_code": "123456",
    #                                     "country_code": "CB"},
    #                                    {"harmonized_system_code": "123",
    #                                     "country_code": "CQ"},
    #                                    {"harmonized_system_code": "457",
    #                                     "country_code": "CE"}
    #                                ]})
