from app import db
from sqlalchemy.dialects.postgresql import JSON

class AdminBusiness(db.Model):
    __tablename__ = 'admin_business'
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), primary_key=True)
    role = db.Column(db.String())
    admin = db.relationship("Admin", back_populates="businesses")
    business = db.relationship("Business", back_populates="admins")
class Business(db.Model):
    __tablename__ = 'businesses'

    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String())
    industry = db.Column(db.String())
    name = db.Column(db.String())
    admins = db.relationship("AdminBusiness", back_populates="business")

    def __init__(self, owner, industry, name):
        self.owner = owner
        self.industry = industry
        self.name = name

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    email = db.Column(db.String())
    mobile = db.Column(db.String())
    businesses = db.relationship("AdminBusiness", back_populates="admin")
    
    def __init__(self, email, first_name, last_name, mobile):
        self.email=email
        self.first_name=first_name
        self.last_name=last_name
        self.mobile=mobile

    def __repr__(self):
        return '<id {}>'.format(self.id)
