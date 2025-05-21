from app.models import Mechanic, ServiceTicket
from app.exstensions import ma
from marshmallow import fields


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        load_instance = False
        fields = ("id",)


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = False

    tickets = fields.Pluck(ServiceTicketSchema, "id", many=True,
                           attribute="service_tickets", dump_only=True)
    
    
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
login_schema = MechanicSchema(exclude=['name', 'salary'])