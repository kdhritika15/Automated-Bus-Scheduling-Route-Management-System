from flask_sqlalchemy import SQLAlchemy

# A single shared SQLAlchemy instance, imported by both models and app.py.
# Kept in its own file to avoid circular imports between app.py and models/.
db = SQLAlchemy()
