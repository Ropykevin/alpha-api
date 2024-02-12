import sentry_sdk
from flask import  flash, jsonify, request
from sentry_sdk import capture_exception
from flask_sqlalchemy import SQLAlchemy
from dbs import Product,app,db


sentry_sdk.init(
    dsn="https://ae1085d73eeb378b00f5f8aacb4811e7@o4506695501611008.ingest.sentry.io/4506695661584384",

    # Enable performance monitoring
    enable_tracing=True,
)


# @app.before_first_request
# def create_tables():
#     db.create_all()


@app.route("/products", methods=["POST", "GET"])
def prods():
    if request.method == "GET":
        try:
            prods = Product.query.all()
            print(prods)
            flash("Products fetched successfully.")
            return jsonify(prods)
        except Exception as e:
            print(e)
            # capture_exception(e)
            flash("Server error. Try again later.")
            return jsonify({})
    else:
        if request.is_json:
            data = request.json
            return jsonify({"message": "Data received successfully."})
        else:
            return "Data is not JSON."


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)  
