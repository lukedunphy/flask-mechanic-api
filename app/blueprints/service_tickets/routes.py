from flask import request, jsonify
from app.blueprints.service_tickets import service_ticket_bp
from app.blueprints.service_tickets.schemas import service_ticket_schema, ServiceTicket, service_tickets_schema, edit_ticket_schema, return_ticket_schema, part_quant_schema
from marshmallow import ValidationError
from app.models import db, Mechanic, ServiceTicket, Inventory, TicketPart
from sqlalchemy import select, delete
from app.exstensions import cache, limiter

# create service ticket - limited
@service_ticket_bp.route("/", methods=['POST'])
# @limiter.limit("3 per hour")
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
            return jsonify({"message": "invalid mechanic id"}), 404
        
    db.session.add(new_ticket)
    db.session.commit()


    return service_ticket_schema.jsonify(new_ticket), 201


# read service ticekts 
@service_ticket_bp.route("/", methods=['GET'])
# @cache.cached(timeout=60)
def read_service_ticekts():
    query = select(ServiceTicket)
    result = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(result), 200


# update service ticket
@service_ticket_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
def edit_ticket(ticket_id):
    try:
        ticket_edits = edit_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(ServiceTicket).where(ServiceTicket.id == ticket_id)
    ticket = db.session.execute(query).scalars().first()
    if not ticket:
        return jsonify({"message": "service ticket not found"}), 404

    for mechanic_id in ticket_edits['add_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    for mechanic_id in ticket_edits['remove_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    db.session.commit()
    return return_ticket_schema.jsonify(ticket), 200


@service_ticket_bp.route('/<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    query = select(ServiceTicket).where(ServiceTicket.id == ticket_id)
    ticket = db.session.execute(query).scalars().first()

    if not ticket:
        return jsonify({"message": "service ticket not found"}), 404

    db.session.delete(ticket)
    db.session.commit()

    return jsonify({"message": f"Service ticket {ticket_id} deleted"}), 200
    


# add part to ServiceTicket
@service_ticket_bp.route('/<int:ticket_id>/parts', methods=['POST'])
def add_part(ticket_id):
    try:
        data = part_quant_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(ServiceTicket).where(ServiceTicket.id == ticket_id)
    ticket = db.session.execute(query).scalars().first()

    if not ticket:
        return jsonify({"message": "invalid ticket id"}), 404
    
    part_query = select(Inventory).where(Inventory.id == data['part_id'])
    part = db.session.execute(part_query).scalars().first()

    if not part: 
        return jsonify({"message": "invalid part id"}), 404
    
    ticket_part = TicketPart(part_id=data['part_id'], quantity=data['quantity'])
    ticket.ticket_parts.append(ticket_part)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200