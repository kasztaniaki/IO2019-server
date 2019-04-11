from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date


class Pool(Model):
    pool_id = Column(Integer, primary_key=True)
    display_name = Column(String(150), unique=True, nullable=False)
    available_count = Column(Integer)
    enabled = Column(Boolean)
    description = Column(String(500), unique=True, nullable=False)
    OS = Column(String(150), unique=True, nullable=False)

    def __repr__(self):
        return self.name
