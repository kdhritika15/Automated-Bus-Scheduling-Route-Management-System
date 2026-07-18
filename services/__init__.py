def register_blueprints(app):
    """
    Registers all API blueprints on the given Flask app.
    Kept here so app.py doesn't accumulate a growing list of imports
    as more blueprints are added in later phases.
    """
    from routes.bus_routes import bus_bp
    from routes.search_routes import search_bp
    from routes.live_routes import live_bp
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
 
    app.register_blueprint(bus_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(live_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)