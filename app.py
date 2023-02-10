from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import raw_data
from datetime import datetime
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def get_response(data: dict or list) -> json:
    return json.dumps(data), 200, {'Content-Type': 'application/json; charset=utf-8'}


class User(db.Model):
    __tablename__: str = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(50))
    phone = db.Column(db.String(50))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Order(db.Model):
    __tablename__: str = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String())
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Offer(db.Model):
    __tablename__: str = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


with app.app_context():
    db.create_all()

    for usr_data in raw_data.users:
        db.session.add(User(**usr_data))
        db.session.commit()

    for ordr_data in raw_data.orders:
        ordr_data['start_date'] = datetime.strptime(ordr_data['start_date'], '%m/%d/%Y').date()
        ordr_data['end_date'] = datetime.strptime(ordr_data['end_date'], '%m/%d/%Y').date()
        db.session.add(Order(**ordr_data))
        db.session.commit()

    for ofr_data in raw_data.offers:
        db.session.add(Offer(**ofr_data))
        db.session.commit()


@app.route('/users/', methods=['GET', 'POST'])
def get_all_users():
    if request.method == 'GET':
        users = User.query.all()
        result = [user.to_dict() for user in users]
        return get_response(result)
    elif request.method == 'POST':
        user_data = json.loads(request.data)
        db.session.add(User(**user_data))
        db.session.commit()
        return '', 201


@app.route('/users/<int:uid>/', methods=['GET', 'PUT', 'DELETE'])
def functions_with_user(uid: int):
    user = User.query.get(uid)
    if request.method == 'GET':
        return get_response(user.to_dict())
    if request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return '', 204
    if request.method == 'PUT':
        user_data = json.loads(request.data)
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.age = user_data['age']
        user.email = user_data['email']
        user.role = user_data['role']
        user.phone = user_data['phone']
        db.session.add(user)
        db.session.commit()
        return '', 204


@app.route('/orders/', methods=['GET', 'POST'])
def get_all_orders():
    if request.method == 'GET':
        orders = Order.query.all()
        result = []
        for order in orders:
            order_dict = order.to_dict()
            order_dict['start_date'] = str(order_dict['start_date'])
            order_dict['end_date'] = str(order_dict['start_date'])
            result.append(order_dict)
        return get_response(result)
    elif request.method == 'POST':
        order_data = json.loads(request.data)
        db.session.add(Order(**order_data))
        db.session.commit()
        return '', 201


@app.route('/orders/<int:oid>/', methods=['GET', 'PUT', 'DELETE'])
def functions_with_order(oid: int):
    order = Order.query.get(oid)
    if request.method == 'GET':
        order_dict = order.to_dict()
        order_dict['start_date'] = str(order_dict['start_date'])
        order_dict['end_date'] = str(order_dict['start_date'])
        return get_response(order_dict)
    if request.method == 'DELETE':
        db.session.delete(order)
        db.session.commit()
        return '', 204
    if request.method == 'PUT':
        order_data = json.loads(request.data)
        order_data['start_date'] = datetime.strptime(order_data['start_date'], '%Y-%m-%d').date()
        order_data['end_date'] = datetime.strptime(order_data['end_date'], '%Y-%m-%d').date()
        order.name = order_data['name']
        order.description = order_data['description']
        order.start_date = order_data['start_date']
        order.end_date = order_data['end_date']
        order.address = order_data['address']
        order.price = order_data['price']
        order.customer_id = order_data['customer_id']
        order.executor_id = order_data['executor_id']
        db.session.add(order)
        db.session.commit()
        return '', 204


@app.route('/offers/', methods=['GET', 'POST'])
def get_all_offers():
    if request.method == 'GET':
        offers = Offer.query.all()
        result = [offer.to_dict() for offer in offers]
        return get_response(result)
    elif request.method == 'POST':
        offer_data = json.loads(request.data)
        db.session.add(Order(**offer_data))
        db.session.commit()
        return '', 201


@app.route('/offers/<int:oid>/', methods=['GET', 'PUT', 'DELETE'])
def functions_with_offer(oid: int):
    offer = Offer.query.get(oid)
    if request.method == 'GET':
        return get_response(offer.to_dict())
    if request.method == 'DELETE':
        db.session.delete(offer)
        db.session.commit()
        return '', 204
    if request.method == 'PUT':
        offer_data = json.loads(request.data)
        offer.order_id = offer_data['order_id']
        offer.executor_id = offer_data['executor_id']
        db.session.add(offer)
        db.session.commit()
        return '', 204


if __name__ == '__main__':
    app.run()
