from app.models import Customer
from app.exstensions import ma

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
    
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)