from app.models import ServiceTicket
from app.blueprints.inventory.schemas import TicketPartSchema
from app.exstensions import ma
from marshmallow import fields


class PartQuantSchema(ma.Schema):
    part_id = fields.Int(required=True)
    quantity = fields.Int(required=True)


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics = fields.Nested("MechanicSchema", many=True)
    customer = fields.Nested("CustomerSchema")
    ticket_parts = fields.Nested("TicketPartSchema", many=True)
    class Meta:
        model = ServiceTicket
        fields = ("mechanic_ids", "VIN", "service_date", "service_desc", 
                  "customer_id", "mechanics", "customer", "ticket_parts")


class EditTicketSchema(ma.Schema):
    remove_ids = fields.List(fields.Int(), required=True)
    add_ids = fields.List(fields.Int(), required=True)
    class Meta:
        fields = ("add_ids", "remove_ids")


    
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
return_ticket_schema = ServiceTicketSchema(exclude=["customer_id"])
edit_ticket_schema = EditTicketSchema()
part_quant_schema = PartQuantSchema()