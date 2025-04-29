from app.models import TicketPart, Inventory
from app.exstensions import ma
from marshmallow import fields

class TicketPartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TicketPart
        fields = ("part_id", "quantity")


class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        include_relationships = True
    ticket_parts = fields.Nested("TicketPartSchema", many=True)


class CreateInventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        fields = ("id", "name", "price")



ticket_part_schema = TicketPartSchema()
ticket_parts_schema = TicketPartSchema(many=True)

inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)

create_inventory_schema = CreateInventorySchema()
create_inventories_schema = CreateInventorySchema(many=True)