from flask import request, jsonify
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema
from marshmallow import ValidationError
from app.models import Mechanic, db
from sqlalchemy import select, delete
from app.exstensions import cache, limiter


# create mechanic - limited
@mechanics_bp.route("/", methods=['POST'])
@limiter.limit("3 per hour")
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages)
    
    new_mechanic = Mechanic(name=mechanic_data['name'], email=mechanic_data['email'], 
                            phone=mechanic_data['phone'], salary=mechanic_data['salary'])
    
    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.jsonify(new_mechanic), 201


# read all mechanics - cached
@mechanics_bp.route("/", methods=['GET'])
@cache.cached(timeout=60)
def get_mechanics():
    query = select(Mechanic)
    result = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(result), 200


# update mechanic - limited
@mechanics_bp.route("/<int:mechanic_id>", methods=['PUT'])
@limiter.limit("3 per hour")
def update_mechanic(mechanic_id):
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic = db.session.execute(query).scalars().first()

    if mechanic == None:
        return jsonify({"message": "invalid mechanic id"})
    
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in mechanic_data.items():
        setattr(mechanic, field, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200


# delete mechanic - limited
@mechanics_bp.route("/<int:mechanic_id>", methods=['DELETE'])
@limiter.limit("3 per hour")
def delete_mechanic(mechanic_id):
    query = delete(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic = db.session.execute(query)

    if mechanic == None:
        return jsonify({"message": "invalid mechanic id"})
    

    db.session.commit()
    return jsonify({"message":f"successfully deleted mechanic {mechanic_id}"})


@mechanics_bp.route('/popular', methods=['GET'])
def popular_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    mechanics.sort(key= lambda mechanic: len(mechanic.service_tickets), reverse=True)

    return mechanics_schema.jsonify(mechanics)