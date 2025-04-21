from flask import request, jsonify
from app.blueprints.service_tickets import service_ticket_bp
from app.blueprints.service_tickets.schemas import service_ticket_schema, ServiceTicket, service_tickets_schema
from marshmallow import ValidationError
from app.models import db, Mechanic, ServiceTicket
from sqlalchemy import select, delete

# create service ticket
@service_ticket_bp.route("/", methods=['POST'])
def create_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
        print(service_ticket_data)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    
    new_ticket = ServiceTicket(VIN=service_ticket_data['VIN'],
                               service_date=service_ticket_data['service_date'],
                               service_desc=service_ticket_data['service_desc'],
                               customer_id=service_ticket_data['customer_id'])
    
    for mechanic_id in service_ticket_data['mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalar()

        if mechanic:
            new_ticket.mechanics.append(mechanic)
        else:
            return jsonify({"message": "invalid mechanic id"})
        
    db.session.add(new_ticket)
    db.session.commit()


    return service_ticket_schema.jsonify(new_ticket)


# read service ticekts
@service_ticket_bp.route("/", methods=['GET'])
def read_service_ticekts():
    query = select(ServiceTicket)
    result = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(result), 200