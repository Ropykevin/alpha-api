from flask import jsonify
import sentry_sdk
from flask import flash, jsonify, request
from sentry_sdk import capture_exception
from flask_sqlalchemy import SQLAlchemy
from dbs import Product, app, db
from flask_cors import CORS


sentry_sdk.init(
    dsn="https://ae1085d73eeb378b00f5f8aacb4811e7@o4506695501611008.ingest.sentry.io/4506695661584384",

    # Enable performance monitoring
    enable_tracing=True,
)


# @app.before_first_request
# def create_tables():
#     db.create_all()


# store & store products
CORS(app)

@app.route("/products", methods=["POST", "GET"])
def prods():
    if request.method == "GET":
        try:
            prods = Product.query.all()
            p_dict = []
            for prod in prods:
                p_dict.append(
                    {"id": prod.id, "name": prod.name, "price": prod.price})
            return jsonify(p_dict)
        except Exception as e:
            print(e)
            # capture_exception(e)
            return jsonify({})

    elif request.method == "POST":
        if request.is_json:
            try:
                data = request.json
                new_product = Product(name=data.get(
                    'name'), price=data.get('price'))
                db.session.add(new_product)
                db.session.commit()
                r = "Product added successfully." + str(new_product.id)
                res = {"result": r}
                return jsonify(res), 201
            except Exception as e:
                print(e)
                # capture_exception(e)
                return jsonify({"error": "Internal Server Error"}), 500
        else:
            return jsonify({"error": "Data is not JSON."}), 400
    else:
        return jsonify({"error": "Method not allowed."}), 400

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
                "price": prd.price
            })
        else:
            return jsonify({"error": "Product not found."}), 404
    except Exception as e:
        print(e)
        # capture_exception(e)
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
