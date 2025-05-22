from flask import request, jsonify
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema, login_schema
from marshmallow import ValidationError
from app.models import Mechanic, db
from sqlalchemy import select, delete
from app.exstensions import cache, limiter
from app.utils.util import encode_token, token_required



# login route
@mechanics_bp.route('/login', methods=['POST'])
def login():
    try: 
        creds = login_schema.load(request.json)
        email = creds['email']
        password = creds['password']
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == email)
    mechanic = db.session.execute(query).scalars().first()

    if mechanic and mechanic.password == password:
        token = encode_token(mechanic.id)

        return jsonify({
            "status": "success",
            "message": "successfully logged in",
            "token": token
        }), 200

    else:
        return jsonify({"message": "invalid email or password"}), 401


# create mechanic - limited
@mechanics_bp.route("/", methods=['POST'])
# @limiter.limit("3 per hour")
def create_mechanic():
    try:
        data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    exists = db.session.execute(
        select(Mechanic).where(Mechanic.email == data['email'])
    ).scalars().first()

    if exists:
        return jsonify({"error": "Email already asssociated with another account"}), 409
    
    new_mechanic = Mechanic(**data)
    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.jsonify(new_mechanic), 201

# read all mechanics - cached
@mechanics_bp.route("/", methods=['GET'])
def get_mechanics():
    query = select(Mechanic)
    result = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(result), 200


# update mechanic - limited
@mechanics_bp.route("/", methods=['PUT'])
# @limiter.limit("3 per hour")
@token_required
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"message": "mechanic not found"}), 404
    
    try:
        data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, val, in data.items():
        setattr(mechanic, field, val)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200


# delete mechanic - limited
@mechanics_bp.route("/", methods=['DELETE'])
@token_required
def delete_mechanic(mechanic_id):
    result = db.session.execute(
        delete(Mechanic).where(Mechanic.id == mechanic_id)
    )

    if result.rowcount == 0:
        return jsonify({"message": "invalid mechanic id"}), 404
    

    db.session.commit()
    return jsonify({
        "message":f"successfully deleted mechanic {mechanic_id}"
    }), 200


# popular mechanic
@mechanics_bp.route('/popular', methods=['GET'])
def popular_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    mechanics.sort(key= lambda mechanic: len(mechanic.service_tickets), reverse=True)

    return mechanics_schema.jsonify(mechanics), 200