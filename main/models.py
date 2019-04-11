from app import db


class Pool(db.Model):
    pool_id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(150), unique=True, nullable=False)
    available_count = db.Column(db.Integer)
    enabled = db.Column(db.Boolean)
    environment = db.Column(db.String(500), unique=True, nullable=False)
    OS = db.Column(db.String(150), unique=True, nullable=False)

    def __init__(self):
        pass

    def __repr__(self):
        return self.name
