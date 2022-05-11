from flask import Flask, request
from database.database import create_database_instance
from database.crud import *

app = Flask(__name__)
inst = create_database_instance()


@app.route('/')
def home():  # put application's code here
    return 'home'


@app.route('/get')
def _get_inventory():  # put application's code here
    ids = request.args.get('ids').split(",")
    return get_inventory(inst, ids)


@app.route('/create', methods=['POST'])
def _create_inventory():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        json = request.json
        try:
            insert_inventory(inst, **json)
            return f"successfully created inventory with id: {json['id']}"
        except Exception as e:
            print(str(e))
            return "Cannot add new inventory"
    else:
        return 'Content-Type not supported!'


@app.route('/edit', methods=['PUT'])
def _modify_inventory():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        json = request.json
        edit_inventory(inst, json['id'], json)
    else:
        return 'Content-Type not supported!'


@app.route('/delete', methods=['DELETE'])
def _del_inventory():
    id = request.args.get('id')
    try:
        delete_inventory(inst, id)
        return f"deletion of inventory item with id {id} successful"
    except Exception as e:
        print("deletion unsuccessful, " + str(e))
        return "deletion failed"


if __name__ == '__main__':
    app.run()
