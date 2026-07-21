from flask import Blueprint, request, jsonify
from . import db
from .models import User, Task, Item, Comment, RefreshToken, House
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity,
    decode_token
)

api_bp = Blueprint('api', __name__)


# ── helpers ───────────────────────────────────────────────────────────────────

def validate_register(data):
    errors = {}
    username = (data.get('username') or '').strip()
    email    = (data.get('email') or '').strip()
    password = data.get('password') or ''

    if not username or len(username) < 3:
        errors['username'] = 'Must be at least 3 characters.'
    if len(username) > 80:
        errors['username'] = 'Must be 80 characters or fewer.'
    if not email or '@' not in email:
        errors['email'] = 'Must be a valid email address.'
    if not password or len(password) < 8:
        errors['password'] = 'Must be at least 8 characters.'
    if len(password) > 128:
        errors['password'] = 'Must be 128 characters or fewer.'

    return errors, username, email, password


# ── auth ──────────────────────────────────────────────────────────────────────

@api_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON.'}), 400

    errors, username, email, password = validate_register(data)
    if errors:
        return jsonify({'errors': errors}), 422

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists.'}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered.'}), 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    db.session.add(RefreshToken(token=refresh_token, user_id=user.id))
    db.session.commit()

    return jsonify({
        'message':       'User registered successfully.',
        'user':          user.to_dict(),
        'access_token':  access_token,
        'refresh_token': refresh_token,
    }), 201


@api_bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON.'}), 400

    email    = (data.get('email') or '').strip()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password.'}), 401

    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    db.session.add(RefreshToken(token=refresh_token, user_id=user.id))
    db.session.commit()

    return jsonify({
        'user':          user.to_dict(),
        'access_token':  access_token,
        'refresh_token': refresh_token,
    }), 200


@api_bp.route('/refresh', methods=['POST'])
def refresh_token():
    data = request.get_json(silent=True)
    if not data or not data.get('refresh_token'):
        return jsonify({'error': 'Refresh token required.'}), 400

    token_str = data['refresh_token']
    stored = RefreshToken.query.filter_by(token=token_str).first()
    if not stored:
        return jsonify({'error': 'Invalid or revoked refresh token.'}), 401

    try:
        decoded = decode_token(token_str)
        user_id = decoded['sub']
    except Exception:
        return jsonify({'error': 'Invalid or expired refresh token.'}), 401

    new_access = create_access_token(identity=str(user_id))
    return jsonify({'access_token': new_access}), 200


@api_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout_user():
    data = request.get_json(silent=True) or {}
    token_str = data.get('refresh_token')

    if token_str:
        stored = RefreshToken.query.filter_by(token=token_str).first()
        if stored:
            db.session.delete(stored)
            db.session.commit()

    return jsonify({'message': 'Logged out successfully.'}), 200


# ── profile ───────────────────────────────────────────────────────────────────

@api_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404
    return jsonify(user.to_dict()), 200


@api_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON.'}), 400

    if 'name' in data:
        name = str(data['name']).strip()
        if len(name) > 120:
            return jsonify({'error': 'Name must be 120 characters or fewer.'}), 422
        user.name = name

    if 'email' in data:
        email = str(data['email']).strip()
        if '@' not in email:
            return jsonify({'error': 'Invalid email address.'}), 422
        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != user.id:
            return jsonify({'error': 'Email already in use.'}), 409
        user.email = email

    if 'profile_pic' in data:
        user.profile_pic = data['profile_pic']

    if 'password' in data:
        pw = data['password']
        if not pw or len(pw) < 8:
            return jsonify({'error': 'Password must be at least 8 characters.'}), 422
        if len(pw) > 128:
            return jsonify({'error': 'Password must be 128 characters or fewer.'}), 422
        user.set_password(pw)

    db.session.commit()
    return jsonify(user.to_dict()), 200


# ── houses ────────────────────────────────────────────────────────────────────

def validate_house(data):
    errors = {}
    title    = (data.get('title') or '').strip()
    location = (data.get('location') or '').strip()
    price    = data.get('price')

    if not title or len(title) < 3:
        errors['title'] = 'Must be at least 3 characters.'
    if not location:
        errors['location'] = 'Location is required.'
    try:
        price = float(price)
        if price <= 0:
            errors['price'] = 'Must be a positive number.'
    except (TypeError, ValueError):
        errors['price'] = 'Must be a valid number.'

    return errors, title, location, price


@api_bp.route('/houses', methods=['GET'])
def list_houses():
    # public browsing — supports optional filters
    query = House.query
    location = request.args.get('location')
    listing_type = request.args.get('listing_type')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    if location:
        query = query.filter(House.location.ilike(f'%{location}%'))
    if listing_type:
        query = query.filter_by(listing_type=listing_type)
    if min_price:
        query = query.filter(House.price >= float(min_price))
    if max_price:
        query = query.filter(House.price <= float(max_price))

    houses = query.order_by(House.created_at.desc()).all()
    return jsonify([h.to_dict() for h in houses]), 200


@api_bp.route('/houses/mine', methods=['GET'])
@jwt_required()
def my_houses():
    user_id = get_jwt_identity()
    houses = House.query.filter_by(owner_id=user_id).order_by(House.created_at.desc()).all()
    return jsonify([h.to_dict() for h in houses]), 200


@api_bp.route('/houses/<int:house_id>', methods=['GET'])
def get_house(house_id):
    house = House.query.get(house_id)
    if not house:
        return jsonify({'error': 'House not found.'}), 404
    return jsonify(house.to_dict()), 200


@api_bp.route('/houses', methods=['POST'])
@jwt_required()
def create_house():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON.'}), 400

    errors, title, location, price = validate_house(data)
    if errors:
        return jsonify({'errors': errors}), 422

    house = House(
        title=title,
        description=data.get('description'),
        price=price,
        location=location,
        bedrooms=data.get('bedrooms'),
        bathrooms=data.get('bathrooms'),
        house_type=data.get('house_type'),
        listing_type=data.get('listing_type', 'rent'),
        image_url=data.get('image_url'),
        contact_phone=data.get('contact_phone'),
        owner_id=user_id,
    )
    db.session.add(house)
    db.session.commit()

    return jsonify({'message': 'House posted successfully.', 'house': house.to_dict()}), 201


@api_bp.route('/houses/<int:house_id>', methods=['PUT'])
@jwt_required()
def update_house(house_id):
    user_id = get_jwt_identity()
    house = House.query.get(house_id)
    if not house:
        return jsonify({'error': 'House not found.'}), 404
    if str(house.owner_id) != str(user_id):
        return jsonify({'error': 'You can only edit your own listings.'}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON.'}), 400

    for field in ('title', 'description', 'location', 'bedrooms', 'bathrooms',
                  'house_type', 'listing_type', 'image_url', 'contact_phone'):
        if field in data:
            setattr(house, field, data[field])
    if 'price' in data:
        try:
            house.price = float(data['price'])
        except (TypeError, ValueError):
            return jsonify({'error': 'Price must be a valid number.'}), 422

    db.session.commit()
    return jsonify({'message': 'House updated successfully.', 'house': house.to_dict()}), 200


@api_bp.route('/houses/<int:house_id>', methods=['DELETE'])
@jwt_required()
def delete_house(house_id):
    user_id = get_jwt_identity()
    house = House.query.get(house_id)
    if not house:
        return jsonify({'error': 'House not found.'}), 404
    if str(house.owner_id) != str(user_id):
        return jsonify({'error': 'You can only delete your own listings.'}), 403

    db.session.delete(house)
    db.session.commit()
    return jsonify({'message': 'House deleted successfully.'}), 200


# ── health ────────────────────────────────────────────────────────────────────

@api_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200
