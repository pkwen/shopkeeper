import os
from flask import Flask, escape, request, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import graphene
print(os.environ['APP_SETTINGS'])
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import Business
class Query(graphene.ObjectType):
    hello = graphene.String(description='A typical hello world')

    def resolve_hello(self, info):
        return 'World'

schema = graphene.Schema(query=Query)

# class TODO(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.String(200), nullable=False)
#     completed = db.Column(db.Integer, default=0)
#     date_created = db.Column(db.DateTime, default=datetime.utcnow)

#     def __repr__(self):
#         return "<Task %r>" % self.id

@app.route('/')
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

if __name__ == "__main__":
    app.run(debug=True)