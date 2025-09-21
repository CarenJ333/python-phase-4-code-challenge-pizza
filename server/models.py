from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # relationship
    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        back_populates="restaurant",
        cascade="all, delete-orphan"
    )

    # Serialization rules
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address
        }

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # relationship

    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        back_populates="pizza",
        cascade="all, delete-orphan"
    )

    # add serialization rules
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "ingredients": self.ingredients
        }

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)


    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"), nullable=False)

    restaurant = db.relationship("Restaurant", back_populates="restaurant_pizzas")
    pizza = db.relationship("Pizza", back_populates="restaurant_pizzas")

    @validates("price")
    def validate_price(self, key, value):
        if value < 1 or value > 30:
            raise ValueError("Price must be between 1 and 30")
        return value

    def to_dict(self):
        return {
            "id": self.id,
            "price": self.price,
            "pizza_id": self.pizza_id,
            "restaurant_id": self.restaurant_id,
            "pizza": self.pizza.to_dict() if self.pizza else None,
            "restaurant": {
                "id": self.restaurant.id,
                "name": self.restaurant.name,
                "address": self.restaurant.address
            } if self.restaurant else None
        }


    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
    
