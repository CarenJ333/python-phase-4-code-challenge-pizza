#!/usr/bin/env python3
import os
from flask import Flask, request, jsonify
from flask_restful import Api
from flask_migrate import Migrate
from models import db, Restaurant, RestaurantPizza, Pizza

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = db.session.query(Restaurant).all()
    return jsonify([r.to_dict() for r in restaurants]), 200


@app.route("/restaurants/<int:id>", methods=["GET", "DELETE"])
def handle_restaurant(id):
    restaurant = db.session.get(Restaurant, id)

    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    if request.method == "GET":
        response = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": [
                {
                    "id": rp.id,
                    "price": rp.price,
                    "restaurant_id": rp.restaurant_id,
                    "pizza_id": rp.pizza_id,
                    "pizza": rp.pizza.to_dict(),
                }
                for rp in restaurant.restaurant_pizzas
            ],
        }
        return jsonify(response), 200

    elif request.method == "DELETE":
        db.session.delete(restaurant)
        db.session.commit()
        return "", 204


@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = db.session.query(Pizza).all()
    return jsonify([p.to_dict() for p in pizzas]), 200


@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json() or {}

    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    if price is None or pizza_id is None or restaurant_id is None:
        return jsonify({"errors": ["validation errors"]}), 400

    pizza = db.session.get(Pizza, pizza_id)
    restaurant = db.session.get(Restaurant, restaurant_id)
    if not pizza or not restaurant:
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        new_rp = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id,
        )
        db.session.add(new_rp)
        db.session.commit()

        return jsonify(new_rp.to_dict()), 201

    except ValueError:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400

    except Exception:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400


if __name__ == "__main__":
    app.run(port=5555, debug=True)
