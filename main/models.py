from app import db


class Pool(db.Model):
    pool_id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(150), unique=True, nullable=False)
    available_count = db.Column(db.Integer)
    enabled = db.Column(db.Boolean)
    environment = db.Column(db.String(500), unique=True, nullable=False)
    OS = db.Column(db.String(150), unique=True, nullable=False)

    def __init__(self, pool_id, display_name, available_count, enabled, environment, OS):
        self.pool_id = pool_id
        self.display_name = display_name
        self.available_count = available_count
        self.enabled = enabled
        self.environment = environment
        self.OS = OS

    def __repr__(self):
        return self.name

    def print(self):
        print("pool_id: " + self.pool_id + ", display_name: " + self.display_name +
              ", available_count: " + self.available_count + ", enabled: "
              + self.enabled + ", environment: " + self.environment + ", OS: " + self.OS)
