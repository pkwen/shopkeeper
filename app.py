import os
from flask import Flask, escape, request, render_template, abort, json, jsonify, make_response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_migrate import Migrate
from datetime import datetime
from flask_bcrypt import Bcrypt
import pandas as pd
import csv
import uuid
import codecs
import graphene
import flask_login

app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.form:
        user = models.Admin.query.filter_by(email=request.form["email"]).first()
        if user is None or not user.validate(request.form["password"]):
            return make_response({"message": "wrong credentials"})
        flask_login.login_user(user, remember=True)
        # return redirect(url_for("login"))
        return make_response(jsonify(user.serialize()), 200)

@app.route("/setpw", methods=["POST"])
def setpw():
    if request.form:
        user = models.Admin.query.first()
        user.password = request.form["password"]
        db.session.commit()
    return make_response(jsonify(user.serialize()), 200)

@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve

    """
    return models.Admin.query.get(user_id)


#product
@app.route("/products", methods=["GET", "POST"])
def products():
    if request.method == "GET":
        branch = models.Branch.query.filter_by(uuid = request.args.get("branch")).first()
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

@app.route("/products/upload_csv", methods=["POST"])
def upload_csv():
    print(flask_login.current_user.businesses)
    flask_file = request.files["file"]
    branch = request.form["branch"]
    if not flask_file:
        return "Upload a CSV file"
    if not branch:
        return "Branch missing"
    data = pd.read_csv(request.files["file"])
    data.insert(2, "branch_id", branch)
    data["uuid"] = [str(uuid.uuid4()) for _ in data["name"]]
    data["description"] = data["description"].apply(lambda desc:[desc])
    data.to_sql("products", engine, if_exists="append", index=False)
    return data.to_json()

    
#station
@app.route("/stations", methods=["GET", "POST"])
def stations():
    if request.method == "GET":
        if not request.args.get("branch"):
            return "Branch missing"
        branch = models.Branch.query.filter_by(uuid = request.args.get("branch")).first()
        return make_response(jsonify(list(map(lambda station: station.serialize(), branch.stations))))
    elif request.method == "POST":
        stn = models.Station(codename="table_4", capacity=2, branch_id=1)
        db.session.add(stn)
        db.session.commit()
        return stn.serialize()

@app.route("/station/<uuid:int>")
def get_station():
    return models.Station.query.filter_by(uuid = uuid).first()

#order
@app.route("/orders", methods=["GET", "POST"])
def orders():
    if request.method == "GET":
        if not request.args.get("branch"):
            return "Branch missing"
        branch = models.Branch.query.filter_by(uuid = request.args.get("branch")).first()
        return make_response(jsonify(list(map(lambda order: order.serialize(), branch.orders))))
    elif request.method == "POST":
        if not request.form["products"] or not request.form["station"] or not request.form["branch"]:
            return "Parameter missing"
        products = json.loads(request.form["products"])
        order = models.Order(total=0, station_id=request.form["station"], branch_id=request.form["branch"])
        total = 0
        for item in products:
            op = models.OrderProduct(quantity=item["quantity"])
            product = models.Product.query.filter_by(uuid = item["uuid"]).first()
            op.product_id = product.id
            order.products.append(op)
            total += product.price * item["quantity"]
        order.total = total
        db.session.add(order)
        db.session.commit()
        return order.serialize()

@app.route("/order/<uuid:int>")
def get_order():
    return models.Order.query.filter_by(uuid = uuid).first()

if __name__ == "__main__":
    app.run(debug=True)