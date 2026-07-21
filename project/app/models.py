from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    name          = db.Column(db.String(120))
    profile_pic   = db.Column(db.Text)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    tasks          = db.relationship('Task', backref='user', lazy=True)
    comments       = db.relationship('Comment', backref='user', lazy=True)
    refresh_tokens = db.relationship('RefreshToken', backref='user', lazy=True)
    houses         = db.relationship('House', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id':          self.id,
            'username':    self.username,
            'email':       self.email,
            'name':        self.name,
            'profile_pic': self.profile_pic,
            'created_at':  self.created_at.isoformat(),
        }


class Task(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255))
    due_date    = db.Column(db.String(120))
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id':          self.id,
            'title':       self.title,
            'description': self.description,
            'due_date':    self.due_date,
            'user_id':     self.user_id,
        }


class Item(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255))
    category    = db.Column(db.String(50))
    comments    = db.relationship('Comment', backref='item', lazy=True)

    def to_dict(self):
        return {
            'id':          self.id,
            'name':        self.name,
            'description': self.description,
            'category':    self.category,
        }


class Comment(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)

    def to_dict(self):
        return {
            'id':      self.id,
            'content': self.content,
            'user_id': self.user_id,
            'item_id': self.item_id,
        }


class House(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(120), nullable=False)
    description  = db.Column(db.String(1000))
    price        = db.Column(db.Float, nullable=False)
    location     = db.Column(db.String(200), nullable=False)
    bedrooms     = db.Column(db.Integer)
    bathrooms    = db.Column(db.Integer)
    house_type   = db.Column(db.String(50))     # e.g. Apartment, Bungalow, Duplex
    listing_type = db.Column(db.String(20), default='rent')  # 'rent' or 'sale'
    image_url    = db.Column(db.Text)
    contact_phone = db.Column(db.String(50))
    owner_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':            self.id,
            'title':         self.title,
            'description':   self.description,
            'price':         self.price,
            'location':      self.location,
            'bedrooms':      self.bedrooms,
            'bathrooms':     self.bathrooms,
            'house_type':    self.house_type,
            'listing_type':  self.listing_type,
            'image_url':     self.image_url,
            'contact_phone': self.contact_phone,
            'owner_id':      self.owner_id,
            'owner_name':    (self.owner.name or self.owner.username) if self.owner else None,
            'created_at':    self.created_at.isoformat() if self.created_at else None,
        }


class RefreshToken(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    token   = db.Column(db.String(512), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
