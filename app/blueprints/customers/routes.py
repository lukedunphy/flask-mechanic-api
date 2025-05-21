from flask import request, jsonify
from app.blueprints.customers import customers_bp
from .schemas import customer_schema, customers_schema, login_schema
from marshmallow import ValidationError
from app.models import Customer, db
from sqlalchemy import select, delete
from app.exstensions import cache, limiter
from app.utils.util import encode_token, token_required


# routes
# login route
@customers_bp.route('/login', methods=['POST'])
def login():
    try: 
        credentials = login_schema.load(request.json)
        email = credentials['email']
        password = credentials['password']
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == email)
    customer = db.session.execute(query).scalars().first()

    if customer and customer.password == password:
        token = encode_token(customer.id)

        response = {
            "status": "success",
            "message": "successfully logged in",
            "token": token
        }

        return jsonify(response), 200
    
    else:
        return jsonify({"message": "invalid email or password"}), 401


# create customer
# limited to defend from DDOS attacks
@customers_bp.route("/", methods=['POST'])
@limiter.limit("5 per hour")
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'],
                             phone=customer_data['phone'], password=customer_data['password'])

    db.session.add(new_customer)
    db.session.commit()

    return customer_schema.jsonify(new_customer), 201


# read all customers 
# added caching because data does not change every second and 60 second timeout 
# should not cause any user issues
@customers_bp.route("/", methods=['GET'])
# @cache.cached(timeout=60)
def get_customers():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Customer)
        customers = db.paginate(query, page=page, per_page=per_page)
        return customers_schema.jsonify(customers)
    except:
        query = select(Customer)
        result = db.session.execute(query).scalars().all()
        return customers_schema.jsonify(result), 200
    

# read customer
@customers_bp.route("/<int:customer_id>", methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer:
        return customer_schema.jsonify(customer), 200
    
    return jsonify({"error": "invalid customer id"}), 400
    
    
# update customer 
@customers_bp.route("/", methods=['PUT'])
@token_required
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
@customers_bp.route("/", methods=['DELETE'])
@token_required
def delete_customer(customer_id):
    customer = db.session.scalar(select(Customer).where(Customer.id == customer_id))

    if not customer:
        return jsonify({"message": f"invalid customer id"}), 404
    
    
    db.session.delete(customer)
    db.session.commit()

    return jsonify({"message": f"successfully deleted customer {customer_id}"})


# search by email
@customers_bp.route("/search", methods=['GET'])
def search_by_email():
    email = request.args.get("email")
    query = select(Customer).where(Customer.email.like(f"%{email}%"))
    customer = db.session.execute(query).scalars().all()
    return customers_schema.jsonify(customer)