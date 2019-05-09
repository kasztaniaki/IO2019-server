from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, exc as sa_exc
import json
from settings import app

db = SQLAlchemy(app)


class SoftwareList(db.Model):
    __tablename__ = "SoftwareList"

    PoolID = db.Column(db.Integer, db.ForeignKey("Pool.ID"), primary_key=True)
    SoftwareID = db.Column(db.Integer, db.ForeignKey("Software.ID"), primary_key=True)
    Version = db.Column(db.String(80), primary_key=True)
    Software = db.relationship("Software")


class Pool(db.Model):
    __tablename__ = "Pool"

    ID = db.Column(db.String(80), primary_key=True)
    Name = db.Column(db.String(80), nullable=False)
    MaximumCount = db.Column(db.Integer)
    Description = db.Column(db.String(80))
    Enabled = db.Column(db.Boolean)
    OSID = db.Column(db.Integer, db.ForeignKey("OperatingSystem.ID"))
    Software = db.relationship("SoftwareList")

    @staticmethod
    def get_pool(pool_id):
        return Pool.query.filter(Pool.ID == pool_id).first()

    @staticmethod
    def add_pool(pool_id, name, maximum_count, description, enabled):
        try:
            pool = Pool(
                ID=pool_id,
                Name=name,
                MaximumCount=maximum_count,
                Description=description,
                Enabled=enabled,
            )
            db.session.add(pool)
            db.session.commit()
        except sa_exc.IntegrityError:
            print("Pool with ID:'" + pool.ID + "' already exists")

        return pool

    def get_software_list(self, software=None):
        if software is None:
            return SoftwareList.query.filter(
                SoftwareList.PoolID == self.ID
            ).with_entities(Software.ID, Software.Name, SoftwareList.Version).join(Software).all()
        else:
            return SoftwareList.query.filter(
                SoftwareList.PoolID == self.ID,
                SoftwareList.SoftwareID == software.ID
            ).with_entities(Software.ID, Software.Name, SoftwareList.Version).join(Software).all()

    def add_software(self, software, version=""):
        try:
            installed_software = SoftwareList(
                PoolID=self.ID,
                SoftwareID=software.ID,
                Version=version
            )
            db.session.add(installed_software)
            db.session.commit()
        except sa_exc.IntegrityError:
            print("Software '" + software.Name + "' already installed")

    def remove_software(self, software, version=None):
        if version is None:
            SoftwareList.query.filter(
                SoftwareList.PoolID == self.ID,
                SoftwareList.SoftwareID == software.ID
            ).delete()
        else:
            SoftwareList.query.filter(
                SoftwareList.PoolID == self.ID,
                SoftwareList.SoftwareID == software.ID,
                SoftwareList.Version == version
            ).delete()
        db.session.commit()

    def update_software(self, software, old_version, new_version):
        if old_version != new_version:
            self.add_software(software, new_version)
            self.remove_software(software, old_version)
            db.session.commit()

    def get_operating_system(self):
        return OperatingSystem.query.filter(OperatingSystem.ID == self.OSID).first()

    def set_operating_system(self, operating_system):
        self.OSID = operating_system.ID
        db.session.commit()

    @staticmethod
    def get_table():
        return [Pool.json(pool) for pool in Pool.query.all()]

    def json(self):
        return {
            "ID": self.ID,
            "Name": self.Name,
            "MaximumCount": self.MaximumCount,
            "Enabled": self.Enabled,
            "OSName": self.get_operating_system().Name,
            "InstalledSoftware": [
                (software.Name, software.Version) for software in self.get_software_list()
            ],
        }

    def __repr__(self):
        pool_object = {
            "ID": self.ID,
            "Name": self.Name,
            "MaximumCount": self.MaximumCount,
        }
        return json.dumps(pool_object)
    

class Software(db.Model):
    __tablename__ = "Software"

    ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)

    @staticmethod
    def get_software(software_id):
        return Software.query.filter(Software.ID == software_id).first()

    @staticmethod
    def add_software(software_name):
        software = Software.query.filter(Software.Name == software_name).first()

        if software is None:
            software = Software(Name=software_name)
            db.session.add(software)
            db.session.commit()
        else:
            print("Software '" + software.Name + "' already exists")

        return software


class OperatingSystem(db.Model):
    __tablename__ = "OperatingSystem"
    ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80), nullable=False)
    PoolList = db.relationship("Pool", backref="owner")

    @staticmethod
    def get_operating_system(os_id):
        return OperatingSystem.query.filter(OperatingSystem.ID == os_id).first()

    @staticmethod
    def add_operating_system(name):
        operating_system = OperatingSystem.query.filter(OperatingSystem.Name == name).first()

        if operating_system is None:
            operating_system = OperatingSystem(Name=name)
            db.session.add(operating_system)
            db.session.commit()
        else:
            print("Operating System '" + operating_system.Name + "' already exists")
        return operating_system
