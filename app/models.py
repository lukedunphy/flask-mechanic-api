from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from typing import List

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


# models
service_mechanics = db.Table(
    "service_mechanics",
    Base.metadata,
    db.Column("ticket_id", db.ForeignKey("service_tickets.id", ondelete="CASCADE")),
    db.Column("mechanic_id", db.ForeignKey("mechanics.id", ondelete="CASCADE"))
)


class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100))
    email: Mapped[str] = mapped_column(db.String(150))
    phone: Mapped[str] = mapped_column(db.String(13))

    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(back_populates='customer', cascade="all, delete")


class ServiceTicket(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    VIN: Mapped[str] = mapped_column(db.String(50))
    service_date: Mapped[date]
    service_desc: Mapped[str] = mapped_column(db.String(250))
    customer_id: Mapped[int] = mapped_column(db.ForeignKey("customers.id", ondelete="CASCADE"))

    customer: Mapped["Customer"] = db.relationship("Customer", back_populates='service_tickets')
    mechanics: Mapped[List["Mechanic"]] = db.relationship(secondary=service_mechanics, back_populates="service_tickets", passive_deletes=True)


class Mechanic(Base):
    __tablename__ = 'mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100))
    email: Mapped[str] = mapped_column(db.String(150))
    phone: Mapped[str] = mapped_column(db.String(13))
    salary: Mapped[int]

    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(secondary=service_mechanics, back_populates="mechanics", cascade="all, delete", passive_deletes=True)