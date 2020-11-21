from app import db
from sqlalchemy.dialects.postgresql import JSON


class Business(db.Model):
    __tablename__ = 'businesses'

    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String())
    industry = db.Column(db.String())
    name = db.Column(db.String())

    def __init__(self, owner, industry, name):
        self.owner = owner
        self.industry = industry
        self.name = name

    def __repr__(self):
        return '<id {}>'.format(self.id)