from app.models import ServiceTicket
from app.exstensions import ma
from marshmallow import fields

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        fields = ("mechanic_ids", "VIN", "service_date", "service_desc", "customer_id")
    
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)