from flask import request, jsonify
from app.blueprints.customers import customers_bp
from .schemas import customer_schema, customers_schema
from marshmallow import ValidationError
from app.models import Customer, db
from sqlalchemy import select, delete


# routes

# create customer
@customers_bp.route("/", methods=['POST'])
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])

    db.session.add(new_customer)
    db.session.commit()

    return customer_schema.jsonify(new_customer), 201


# read all customers
@customers_bp.route("/", methods=['GET'])
def get_customers():
    query = select(Customer)
    result = db.session.execute(query).scalars().all()
    return customers_schema.jsonify(result), 200


# update customer
@customers_bp.route("/<int:customer_id>", methods=['POST'])
def update_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()

    if customer == None:
        return jsonify({"message": "invalid customer id"})
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in customer_data.items():
        setattr(customer, field, value)

    db.session.execute(query)
    db.session.commit()

    return customer_schema.jsonify(customer), 200


# delete customer
@customers_bp.route("/<int:customer_id>", methods=['DELETE'])
def delete_customer(customer_id):
    customer = db.session.scalar(select(Customer).where(Customer.id == customer_id))

    if not customer:
        return jsonify({"message": f"invalid customer id"}), 404
    
    
    db.session.delete(customer)
    db.session.commit()

    return jsonify({"message": f"successfully deleted customer {customer_id}"})