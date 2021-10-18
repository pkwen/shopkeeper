import os
from flask import Flask, escape, request, render_template, abort, json, jsonify, make_response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_migrate import Migrate
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask_cors import CORS
from decimal import Decimal
import pandas as pd
import csv
import uuid
import codecs
import graphene

app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)
CORS(app)
engine = create_engine(os.environ["DATABASE_URL"])

import models
class Query(graphene.ObjectType):
    hello = graphene.String(description="A typical hello world")

    def resolve_hello(self, info):
        return "World"

schema = graphene.Schema(query=Query)

# class TODO(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.String(200), nullable=False)
#     completed = db.Column(db.Integer, default=0)
#     date_created = db.Column(db.DateTime, default=datetime.utcnow)

#     def __repr__(self):
#         return "<Task %r>" % self.id

# GraphQL code example:
@app.route("/")
def hello():
    query = """
    query SayHello {
      hello
    }
    """
    # name = request.args.get("name")
    # print(schema.execute(query).data["hello"])
    return render_template("index.html", res=schema.execute(query).data["hello"])
    # return f"Hi {name}"
    
    
@app.route("/hidden/<int:index>")
def secret(index):
    return render_template("dynamic.html", index=index)

@app.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    user = models.Admin.query.filter_by(email=request.json["email"]).first()
    if user is None or not user.validate(password):
        return make_response(jsonify({"message": "wrong credentials"}, 401))

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=email)
    return make_response(jsonify(access_token=access_token), 200)
    # if request.json:
    #     user = models.Admin.query.filter_by(email=request.json["email"]).first()
    #     if user is None or not user.validate(request.json["password"]):
    #         return make_response(jsonify({"message": "wrong credentials"}, 200))
        
    #     # return redirect(url_for("login"))
    #     return make_response(jsonify(user.serialize()), 200)
    # else:
    #     return make_response(jsonify({'message': 'params not found'}, 200))


@app.route('/current_user', methods=["GET"])
@jwt_required
def current_user():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user)

@app.route("/logout", methods=["POST"])
@jwt_required
def logout():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user)
    # if :
        
    #     return make_response({}, 200)
    # else:
        # return "Not currently logged in"

@app.route("/setpw", methods=["POST"])
def setpw():
    if request.form:
        user = models.Admin.query.first()
        user.password = request.form["password"]
        db.session.commit()
    return make_response(jsonify(user.serialize()), 200)

#product
@app.route("/products", methods=["GET", "POST"])
def products():
    if request.method == "GET":
        branch = models.Branch.query.filter_by(id = request.args.get("branch_id")).first()
        if branch:
            return make_response(jsonify(list(map(lambda product: product.serialize(), branch.products))), 200)
        else:
            return "Branch not found"
    elif request.method == "POST":
        # validate form
        product = models.Product(
            name="One",
            quantity=500,
            price=12.99,
            description="yes"
        )
        db.session.add(product)
        db.session.commit()
        return make_response(jsonify(product.serialize()), 200)

@app.route("/products_by_category")
def products_by_category():
    branch_id = request.args.get("branch_id")
    if not branch_id:
        return {}
    else:
        return make_response(jsonify(models.Product.list_by_category(branch_id)))

@app.route("/products/upload_csv", methods=["POST"])
@jwt_required
def upload_csv():
    print(request)
    # breakpoint()
    # if not flask_login.current_user.is_authenticated:
    #     return "Need to be logged in to perform this action"
    flask_file = request.files
    branch_id = request.args.get("branch_id")
    if not flask_file:
        return "Upload a CSV file"
    if not branch_id:
        return "Branch missing"
    data = pd.read_csv(request.files["file"])
    branch_id = models.Branch.query.filter_by(id = branch_id).first().id
    if not branch_id:
        return "Cannot find branch"
    existing_products = models.Product.query.filter((models.Product.branch_id == branch_id) & (models.Product.name.in_(data["name"]))).all()
    # deactivate products that aren't in csv
    db.session.query(models.Product).filter((models.Product.branch_id == branch_id) & (~models.Product.name.in_(data["name"]))).update({"state": "unavailable"}, synchronize_session="fetch")
    for ep in existing_products:
        np = data[data["name"] == ep.name].to_dict("records")[0]
        ep.price = np["price"]
        ep.description = np["description"].splitlines() if type(np["description"]) is str else []
        ep.stock = np["stock"]
        ep.category = np["category"]
        ep.state = "available"
        db.session.merge(ep)
    db.session.commit()
        
    # only overwrite new unique products
    data = data[~data["name"].isin([product.name for product in existing_products])]
    if not data.empty:
        data.insert(2, "branch_id", branch_id)
        data["id"] = [str(uuid.uuid4()) for _ in data["name"]]
        data["description"] = data["description"].apply(lambda desc:desc.splitlines() if type(desc) is str else [])
        data.to_sql("products", engine, if_exists="append", index=False)

    updated_products = models.Product.query.filter_by(branch_id=branch_id, state="available").all()
    print(updated_products)
    return make_response(jsonify(list(map(lambda product: product.serialize(), updated_products))), 200)

    
#station
@app.route("/stations", methods=["GET", "POST"])

def stations():
    if request.method == "GET":
        if not request.args.get("branch_id"):
            return "Branch missing", 400
        branch = models.Branch.query.filter_by(id = request.args.get("branch_id")).first()
        if not branch:
            return []
        return make_response(jsonify(list(map(lambda station: station.serialize(), branch.stations))))
    elif request.method == "POST":
        print(request.json)
        if not request.json["codename"] or not request.json["capacity"] or not request.json["branch_id"]:
            return "Parameter missing", 400
        stn = models.Station(
            codename=request.json['codename'], 
            capacity=request.json['capacity'], 
            branch_id=request.json['branch_id']
        )
        db.session.add(stn)
        db.session.commit()
        return stn.serialize()

@app.route("/stations/<uuid:int>")
def get_station():
    return models.Station.query.filter_by(id = uuid).first().serialize()

#order
@app.route("/orders", methods=["GET", "POST"])
def orders():
    if request.method == "GET":
        branch_id = request.args.get("branch_id")
        if not branch_id:
            return "Branch missing"
        branch = models.Branch.query.filter_by(id = branch_id).first()
        return make_response(jsonify(list(map(lambda order: order.serialize(), branch.orders))))
    elif request.method == "POST":
        if not request.json["products"] or not request.json["station_id"] or not request.json["branch_id"]:
            return "Parameter missing"
        products = request.json["products"]
        order = models.Order(total=0, station_id=request.json["station_id"], branch_id=request.json["branch_id"])
        total = 0
        for item in products:
            op = models.OrderProduct(quantity=item["quantity"])
            product = models.Product.query.filter_by(id = item["id"]).first()
            op.product_id = product.id
            order.products.append(op)
            total += Decimal.from_float(product.price) * Decimal.from_float(item["quantity"])
            if len(item["selectedCustomizations"]) > 0:
                for customization in item["selectedCustomizations"]:
                    opc = models.OrderProductCustomization()
                    opc.customization_id = customization["id"]
                    op.customizations.append(opc)
                    total += Decimal.from_float(customization["price"]) * Decimal.from_float(item["quantity"])

        order.total = total
        db.session.add(order)
        db.session.commit()
        return order.serialize()

@app.route("/order/<uuid:int>")
def get_order():
    return models.Order.query.filter_by(id = uuid).first().serialize()

if __name__ == "__main__":
    app.run(debug=True)