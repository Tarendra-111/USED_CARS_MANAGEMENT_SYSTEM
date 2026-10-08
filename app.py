from flask import Flask, render_template
from config import Config
from database.mongodb import create_indexes

from routes.cars import cars_bp
from routes.sellers import sellers_bp
from routes.customers import customers_bp
from routes.inspections import inspections_bp
from routes.enquiries import enquiries_bp
from routes.test_drives import test_drives_bp
from routes.sales import sales_bp
from routes.payments import payments_bp
from routes.ownership_transfers import transfers_bp
from routes.employees import employees_bp
from routes.analytics import analytics_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    for bp in (cars_bp, sellers_bp, customers_bp, inspections_bp, enquiries_bp,
               test_drives_bp, sales_bp, payments_bp, transfers_bp, employees_bp, analytics_bp):
        app.register_blueprint(bp)

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(_e):
        # Never leak raw Mongo/Python tracebacks to the browser
        return {"success": False, "error": "Internal server error"}, 500

    with app.app_context():
        create_indexes()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG)
