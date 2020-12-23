from app import db, bcrypt, login_manager, jsonify
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from flask_login import UserMixin
import enum

import uuid

    
class Admin(UserMixin, db.Model):
    __tablename__ = "admins"
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    email = db.Column(db.String(), unique=True)
    _password = db.Column(db.LargeBinary())
    mobile = db.Column(db.String(), unique=True)
    businesses = db.relationship("AdminBusiness", back_populates="admin")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __repr__(self):
        return "<id {}>".format(self.id)
    
    def serialize(self):
        return {
            "email": self.email
        }
    
    @hybrid_property
    def password(self):
        return self._password
    
    @password.setter
    def password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)
        
    @hybrid_method
    def validate(self, plaintext_password):
        return bcrypt.check_password_hash(self.password, plaintext_password)
        
@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve

    """
    return Admin.query.get(user_id)

class Business(db.Model):
    __tablename__ = "businesses"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    owner = db.Column(db.String())
    industry = db.Column(db.String())
    name = db.Column(db.String())
    admins = db.relationship("AdminBusiness", back_populates="business")
    branches = db.relationship("Branch", back_populates="business")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __init__(self, owner, industry, name):
        self.owner = owner
        self.industry = industry
        self.name = name

    def __repr__(self):
        return "<id {}>".format(self.id)


class AdminBusiness(db.Model):
    __tablename__ = "admin_business"
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"), primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey("businesses.id"), primary_key=True)
    role = db.Column(db.String())
    admin = db.relationship("Admin", back_populates="businesses")
    business = db.relationship("Business", back_populates="admins")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    
class Branch(db.Model):
    __tablename__ = "branches"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String())
    location = db.Column(db.String())
    business_id = db.Column(db.Integer, db.ForeignKey("businesses.id"))
    business = db.relationship("Business", back_populates="branches")
    stations = db.relationship("Station", back_populates="branch")
    products = db.relationship("Product")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    
class FoodEnum(enum.Enum):
    starter = 0
    
    
class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String)
    stock = db.Column(db.Integer)
    price = db.Column(db.Float)
    category = db.Column(db.String)
    description = db.Column(db.ARRAY(db.Text), default=[])
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"))
    branch = db.relationship("Branch")
    components = db.relationship("ProductComponent", back_populates="product")
    orders = db.relationship("OrderProduct", back_populates="product")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "stock": self.stock,
            "price": self.price,
            "description": self.description,
            "branch": self.branch_id
        }
    
class ProductComponent(db.Model):
    __tablename__ = "products_components"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    component_id = db.Column(db.Integer, db.ForeignKey("components.id"))
    quantity = db.Column(db.Integer)
    product = db.relationship("Product", back_populates="components")
    component = db.relationship("Component", back_populates="products")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    
class Component(db.Model):
    __tablename__ = "components"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String)
    unit = db.Column(db.String)
    stock = db.Column(db.Integer)
    cost = db.Column(db.Float)
    supplier = db.Column(db.String)
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"))
    products = db.relationship("ProductComponent", back_populates="component")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    
class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    total = db.Column(db.Float)
    status = db.Column(db.String, default="requested")
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"))
    products = db.relationship("OrderProduct", back_populates="order")
    station_id = db.Column(db.Integer, db.ForeignKey("stations.id"))
    station = db.relationship("Station", back_populates="orders")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    
    def serialize(self):
        return {
            "uuid": self.uuid,
            "total": self.total,
            "station": self.station.codename
        }
    
class OrderProduct(db.Model):
    __tablename__ = "orders_products"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    order = db.relationship("Order", back_populates="products")
    product = db.relationship("Product", back_populates="orders")
    quantity = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    
class Station(db.Model):
    __tablename__ = "stations"
    id = db.Column(db.Integer, primary_key=True)
    codename = db.Column(db.String)
    capacity = db.Column(db.Integer)
    qr_code_img = db.Column(db.String)
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    qr_code_content = db.Column(db.String)
    branch_id = db.Column(db.Integer, db.ForeignKey("branches.id"))
    branch = db.relationship("Branch", back_populates="stations")
    orders = db.relationship("Order", back_populates="station")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    
    def serialize(self):
        return {
            "codename": self.codename,
            "capacity": self.capacity
        }
    
