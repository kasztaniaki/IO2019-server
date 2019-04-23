from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
import json
from settings import app


db = SQLAlchemy(app)


class Pool(db.Model):
    __tablename__ = 'Pools'
    PoolID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80), nullable=False)
    DisplayName = db.Column(db.String(80), nullable=False)
    MaximumCount = db.Column(db.Integer)
    Description = db.Column(db.String(80))
    Enabled = db.Column(db.Integer)
    InstalledSoftware = db.relationship('InstalledSoftware', backref='owner')
    OSID = db.Column(db.Integer, db.ForeignKey('OperatingSystems.OSID'))
    __table_args__ = (
        CheckConstraint(Enabled >= 0, Enabled <= 1),
        {})

    def json(self):
        OS = OperatingSystem.query.filter(OperatingSystem.OSID == self.OSID).all()[0]
        return {'PoolID': self.Name, 'DisplayName': self.DisplayName, 'MaximumCount': self.MaximumCount,
                'Enabled': self.Enabled, 'OSName': OS.Name,
                'OSVersion': OS.Version, 'InstalledSoftware': [(software.Name, software.Version) for software in self.InstalledSoftware]}


    @staticmethod
    def add_pool( _name, _maximumcount, _description, other):
        new_pool = Pool(Name=_name, MaximumCount=_maximumcount, Description=_description,
                        SoftwareList=[other])
        db.session.add(new_pool)
        db.session.commit()

    @staticmethod
    def add_detailed_pool( _pool_name,_pool_display_name,_pool_maximumcount, _pool_description, _so_name, _so_language, _so_version, _soft_name, _soft_version):
        new_soft = InstalledSoftware(Name=_soft_name, Version=_soft_version)
        new_pool = Pool(Name=_pool_name, DisplayName=_pool_display_name, MaximumCount=_pool_maximumcount, Description=_pool_description,
                        InstalledSoftware =[new_soft])
        new_operating_system = OperatingSystem(Name=_so_name, Language=_so_language, Version=_so_version, PoolList=[new_pool])
        db.session.add(new_operating_system)
        db.session.commit()


    @staticmethod
    def get_pools():
        return [Pool.json(pool) for pool in Pool.query.all()]

    def __repr__(self):
        pool_object = {
            'Name': self.Name,
            'Maximumcount': self.MaximumCount,
            'Description': self.Description
        }
        return json.dump(pool_object)


class InstalledSoftware(db.Model):
    __tablename__ = 'InstalledSoftwares'

    SoftwareID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)
    Version= db.Column(db.String)
    PoolID = db.Column(db.Integer, db.ForeignKey('Pools.PoolID'))


    @staticmethod
    def add_software_to_pool(_poolid, _soft_name, _soft_version ):
        new_installed = InstalledSoftware(PoolID=_poolid, Name=_soft_name, Version=_soft_version)
        db.session.add(new_installed)
        db.session.commit()

    def json(self):
        return {'SoftwareID':self.SoftwareID, 'Name': self.Name, 'Version': self.Version }

    @staticmethod
    def get_softwares():
        return [InstalledSoftware.json(soft) for soft in InstalledSoftware.query.all()]


class OperatingSystem(db.Model):
    __tablename__ = 'OperatingSystems'
    OSID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80), nullable=False)
    Language = db.Column(db.String(80), nullable=False)
    Version = db.Column(db.String(80), nullable=False)
    PoolList= db.relationship("Pool", backref='owner')

    @staticmethod
    def add_operating_system(_name, _language, _version):
        new_operating_system = OperatingSystem(Name=_name, Language=_language, Version=_version)
        db.session.add(new_operating_system)
        db.session.commit()








