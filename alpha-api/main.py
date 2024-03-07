from datetime import timedelta
from flask import jsonify
import sentry_sdk
from flask import jsonify, request
from sentry_sdk import capture_exception
from dbs import Product, app, db, Sale, User
from flask_cors import CORS
import jwt
from sqlalchemy import func,desc
from functools import wraps
import datetime

sentry_sdk.init(
    dsn="https://ae1085d73eeb378b00f5f8aacb4811e7@o4506695501611008.ingest.sentry.io/4506695661584384",

    # Enable performance monitoring
    enable_tracing=True,
)

CORS(app)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['username']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route("/products", methods=["POST", "GET"])
@token_required
def prods(current_user):

    print("--------------",current_user)

    if request.method == "GET":
        try:
            prods = Product.query.all()
            p_dict = []
            for prod in prods:
                p_dict.append(
                    {"id": prod.id, "name": prod.name,"cost": prod.cost, "price": prod.price,'username':prod.username})
            return jsonify(p_dict)
        except Exception as e:
            print(e)
            # capture_exception(e)
            return jsonify({})

    elif request.method == "POST":
        if request.is_json:
            try:
                data = request.json

                new_product = Product(
                    name=data['name'], cost=data['cost'], price=data['price'],user_id=)
                db.session.add(new_product)
                db.session.commit()
                r = "Product added successfully. ID: " + str(new_product.id)
                res = {"result": r}
                return jsonify(res), 201
            except Exception as e:
                print(e)
                # capture_exception(e)
                return jsonify({"error": "Internal Server Error"}), 500
        else:
            return jsonify({"error": "Data is not JSON."}), 400


# Task by Thursday
# Get a single product in the route


@app.route('/get-product<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        prd = Product.query.get(product_id)
        if prd:
            return jsonify({
                "id": prd.id,
                "name": prd.name,
                "cost": prd.cost,
                "price": prd.price
            })
        else:
            return jsonify({"error": "Product not found."}), 404
    except Exception as e:
        print(e)
        # capture_exception(e)
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/sales', methods=['GET', 'POST'])
# @token_required
def sales():
    if request.method == 'GET':
        try:
            sales = Sale.query.all()
            s_dict = []
            for sale in sales:
                s_dict.append({"id": sale.id, "pid": sale.pid,
                              "quantity": sale.quantity, "created_at": sale.created_at})
            return jsonify(s_dict)
        except Exception as e:
            print(e)
            # capture_exception(e)
            return jsonify({})

    elif request.method == 'POST':
        if request.is_json:
            try:
                data = request.json
                new_sale = Sale(pid=data.get(
                    'pid'), quantity=data.get('quantity'))
                db.session.add(new_sale)
                db.session.commit()
                s = "sales added successfully." + str(new_sale.id)
                sel = {"result": s}
                return jsonify(sel), 201
            except Exception as e:
                print(e)
                # capture_exception(e)
                return jsonify({"error": "Internal Server Error"}), 500
        else:
            return jsonify({"error": "Data is not JSON."}), 400
    else:
        return jsonify({"error": "Method not allowed."}), 400


@app.route('/dashboard', methods=["GET"])
# @token_required
def dashboard():
    # Query to get sales per day
    sales_per_day = db.session.query(
        func.date(Sale.created_at).label('date'),
        func.sum(Sale.quantity * Product.price).label('total_sales')
    ).join(Product).group_by(
        func.date(Sale.created_at)
    ).all()

    # Convert sales data to JSON format
    sales_data = [{'date': str(day), 'total_sales': sales}
                  for day, sales in sales_per_day]

    # Query to get sales per product
    sales_per_product = db.session.query(
        Product.name,
        func.sum(Sale.quantity * Product.price).label('sales_product')
    ).join(Sale).group_by(
        Product.name
    ).all()

    # Convert sales per product data to JSON format
    salesproduct_data = [{'name': name, 'sales_product': sales_product}
                         for name, sales_product in sales_per_product]

    # Query to get profit per day
    profit_per_day = db.session.query(
        func.date(Sale.created_at).label('date'),
        func.sum((Sale.quantity * Product.price) -
                 (Sale.quantity * Product.cost)).label('total_profit')
    ).join(Product).group_by(
        func.date(Sale.created_at)
    ).all()

    # Convert profit per day data to JSON format
    profit_per_day_data = [{'date': str(day), 'total_profit': profit}
                           for day, profit in profit_per_day]

    # Query to get profit per product
    profit_per_product = db.session.query(
        Product.name,
        func.sum((Sale.quantity * Product.price) -
                 (Sale.quantity * Product.cost)).label('profit_product')
    ).join(Sale).group_by(
        Product.name
    ).all()

    # Convert profit per product data to JSON format
    profit_per_product_data = [{'name': name, 'profit_product': profit}
                               for name, profit in profit_per_product]

    # Query to get recent sales (last 10)
    recent_sales = db.session.query(Sale, Product).\
        join(Product).\
        order_by(Sale.created_at.desc()).\
        limit(10).\
        all()

    # Convert recent sales data to JSON format
    recent_sales_data = [{'id': sale.id, 'name': product.name, 'price': product.price}
                         for sale, product in recent_sales]
    
    
    # Query to get recent products (last 10)
    recent_products = db.session.query(Product).\
        order_by(Product.created_at.desc()).\
        limit(10).\
        all()

    # Convert recent products data to JSON format
    recent_products_data = [{'id': product.id, 'name': product.name, 'price': product.price}
                            for product in recent_products]
    # print(recent_products_data)
    # print(recent_sales)
    # Constructing dashboard data
    dashboard_data = {
        'sales_data': sales_data,
        'salesproduct_data': salesproduct_data,
        'profit_per_day': profit_per_day_data,
        'profit_per_product': profit_per_product_data,
        'recent_sales': recent_sales_data,
        'recent_products': recent_products_data
    }

    return jsonify(dashboard_data)



@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']

    # Check if the username does not exist
    if not User.query.filter_by(username=username).first():
        new_user = User(username=username, password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        r = f"successfully stored userid: {str(new_user.id)}"
        res = {"result": r}
        return jsonify(res), 201
    else:
        return jsonify({'error': f'Username {username} already exists'}), 400


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    # Query the database for the user
    user = User.query.filter_by(username=username, password=password).first()

    if user:

        token = jwt.encode({'username': username, 'exp': datetime.datetime.utcnow()
                            + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'access_token': token}), 200
    else:
        return jsonify({'error': 'User does not exist'}), 404


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
