from flask import request, jsonify
from app.blueprints.inventory import inventory_bp
from app.blueprints.inventory.schemas import inventory_schema, inventories_schema, create_inventory_schema, create_inventories_schema
from marshmallow import ValidationError
from app.models import Inventory, db
from sqlalchemy import select, delete
from app.exstensions import cache, limiter



# create inventory item
@inventory_bp.route('/', methods={'POST'})
def create_inventory():
    try: 
        inventory_data = inventory_schema.load(request.json)
    except  ValidationError as e:
        return jsonify(e.messages), 400
    
    new_item = Inventory(name=inventory_data['name'], price=inventory_data['price'])

    db.session.add(new_item)
    db.session.commit()
    return create_inventory_schema.jsonify(new_item), 201


# read inventory
@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    query = select(Inventory)
    result = db.session.execute(query).scalars().all()

    return create_inventories_schema.jsonify(result), 200


# update inventory
@inventory_bp.route('/<int:item_id>', methods=['PUT'])
def update_inventory(item_id):
    query = select(Inventory).where(Inventory.id == item_id)
    item = db.session.execute(query).scalars().first()
    if not item:
        return jsonify({"message": "invalid id"})
    
    try:
        inventory_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in inventory_data.items():
        setattr(item, field, value)

    db.session.commit()
    return create_inventory_schema.jsonify(item)
    

# delete inventory item
@inventory_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_inventory(item_id):
    result = db.session.execute(
        delete(Inventory).where(Inventory.id == item_id)
    )

    if result.rowcount == 0:
        return jsonify({"message": "invalid id"}), 404

    db.session.commit()
    return jsonify({
        "message": f"successfully deleted inventory item {item_id}"
    }), 200