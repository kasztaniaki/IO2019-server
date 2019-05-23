from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, orm, exc as sa_exc
import json
from settings import app
from datetime import datetime as date

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
    Description = db.Column(db.String(200))
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
            print("Pool with ID:'" + pool_id + "' already exists")
            raise ValueError

        return pool

    @staticmethod
    def remove_pool(pool_id):
        try:
            pool = Pool.query.filter(Pool.ID == pool_id).first()
            software_list = SoftwareList.query.filter(SoftwareList.PoolID == pool_id).all()
            for software in software_list:
                db.session.delete(software)
            db.session.delete(pool)
            db.session.commit()
        except orm.exc.UnmappedInstanceError:
            print("Pool of ID:'" + pool_id + "' doesn't exist")
            raise ValueError

    @staticmethod
    def edit_pool(pool_id, new_id, name, max_count, description, enabled):
        try:
            pool = Pool.query.filter(Pool.ID == pool_id).first()
            pool.ID = new_id
            pool.Name = name
            pool.MaximumCount = max_count
            pool.Description = description
            pool.Enabled = enabled
            db.session.commit()
        except sa_exc.IntegrityError:
            print("Pool with ID:'" + pool_id + "' already exists")
            raise ValueError

        for software in SoftwareList.query.filter(SoftwareList.PoolID == pool_id).all():
            software.PoolID = new_id
            db.session.commit()

        return pool

    def edit_software(self, new_software_list):
        pool = Pool.query.filter(Pool.ID == self.ID).first()
        old_software_list = {tuple(x[1:]) for x in pool.get_software_list()}
        new_software_list = {tuple(x) for x in new_software_list}

        software_to_remove = old_software_list.difference(new_software_list)
        for name, version in software_to_remove:
            pool.remove_software(Software.get_software_by_name(name), version)

        software_to_add = new_software_list.difference(old_software_list)
        for name, version in software_to_add:
            software = Software.add_software(name)
            pool.add_software(software, version)

    # Method below doesn't return list of software objects! Only list with [ID, Name, Version]
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

    def add_software(self, software, version):
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

    def add_reservation(self, user, machine_count, start_date, end_date):
        if machine_count <= 0:
            raise ValueError("Machine count have to greater than 0")

        if self.Enabled is False:
            raise AttributeError("Disabled Pool cannot be reserved")

        free_machines = self.available_machines(start_date, end_date)

        if free_machines-machine_count < 0:
            raise ValueError("There are not enough available machines in given time frame")

        try:
            reservation = Reservation(
                PoolID=self.ID,
                UserID=user.ID,
                StartDate=start_date,
                EndDate=end_date,
                MachineCount=machine_count,
                Cancelled=False
            )

            db.session.add(reservation)
            db.session.commit()

            return reservation
        except sa_exc.IntegrityError:
            print("Reservation of pool nr: " + self.ID + " cannot be added")

    def available_machines(self, start_date, end_date):
        if self.Enabled is False:
            raise AttributeError("Disabled Pool has no available machines")

        taken_machines_array = Reservation.query.filter(
            Reservation.PoolID == self.ID,
            Reservation.StartDate < end_date,
            Reservation.EndDate > start_date,
            Reservation.Cancelled is False
        ).with_entities(Reservation.MachineCount).all()

        taken_machines = 0
        for machines in taken_machines_array:
            taken_machines = taken_machines + machines[0]
        return self.MaximumCount - taken_machines

    @staticmethod
    def get_table():
        return [Pool.json(pool) for pool in Pool.query.all()]

    def json(self):
        try:
            os_name = self.get_operating_system().Name
        except AttributeError:
            os_name = ""

        return {
            "ID": self.ID,
            "Name": self.Name,
            "MaximumCount": self.MaximumCount,
            "Enabled": self.Enabled,
            "OSName": os_name,
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


class User(db.Model):
    __tablename__ = "User"

    ID = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(80), nullable=False, unique=True)
    Password = db.Column(db.String(80))
    Name = db.Column(db.String(80))
    Surname = db.Column(db.String(80))
    IsAdmin = db.Column(db.Boolean)

    @staticmethod
    def get_user(user_id):
        return User.query.filter(User.ID == user_id).first()

    @staticmethod
    def add_user(email, password, name, surname, is_admin=False):
        try:
            user = User(
                Email=email,
                Password=password,
                Name=name,
                Surname=surname,
                IsAdmin=is_admin,
            )
            db.session.add(user)
            db.session.commit()

            return user
        except sa_exc.IntegrityError:
            print("User with email: '" + email + "' already exists")

    def set_email(self, email):
        if email != self.Email:
            try:
                self.Email = email
                db.session.commit()
            except sa_exc.IntegrityError:
                print("Email: '" + self.Email + "' already exists in database")

    def set_password(self, password):
        if password != self.Password:
            self.Password = password
            db.session.commit()

    def set_name(self, name):
        if name != self.Name:
            self.Name = name
            db.session.commit()

    def set_surname(self, surname):
        if surname != self.Surname:
            self.Surname = surname
            db.session.commit()

    def give_admin_permissions(self):
        if self.IsAdmin is True:
            print("User: '" + self.ID + "' already is an admin")
        else:
            self.IsAdmin = True
            db.session.commit()

    def remove_admin_permissions(self):
        if self.IsAdmin is False:
            print("User: '" + self.ID + "' isn't admin")
        else:
            self.IsAdmin = False
            db.session.commit()

    def check_password(self, password):
        if self.Password == password:
            return True
        else:
            return False

    def get_reservations(self, start_date=date(2019, 1, 1), end_date=date(2099, 12, 31), show_cancelled=True):
        reservation_list = []

        if show_cancelled:
            query = Reservation.query.filter(
                Reservation.UserID == self.ID,
                Reservation.StartDate < end_date,
                Reservation.EndDate > start_date,
            ).with_entities(Reservation.ID).all()
        else:
            query = Reservation.query.filter(
                Reservation.UserID == self.ID,
                Reservation.StartDate < end_date,
                Reservation.EndDate > start_date,
                Reservation.Cancelled is False
            ).with_entities(Reservation.ID).all()

        for reservation_id in query:
            reservation = Reservation.get_reservation(reservation_id[0])
            reservation_list.append(reservation)

        return reservation_list

    def json(self):
        return {
            "ID": self.ID,
            "Email": self.Email,
            "Name": self.Name,
            "Surname": self.Surname,
            "IsAdmin": self.IsAdmin
        }

    def __repr__(self):
        user_object = {
            "ID": self.ID,
            "Email": self.Email,
            "Name": self.Name,
            "Surname": self.Surname,
            "IsAdmin": self.IsAdmin
        }
        return json.dumps(user_object)


class Reservation(db.Model):
    __tablename__ = "Reservation"

    ID = db.Column(db.Integer, primary_key=True)
    PoolID = db.Column(db.Integer, db.ForeignKey("Pool.ID"))
    UserID = db.Column(db.Integer, db.ForeignKey("User.ID"))
    StartDate = db.Column(db.DateTime)
    EndDate = db.Column(db.DateTime)
    MachineCount = db.Column(db.Integer)
    Cancelled = db.Column(db.Boolean)
    User = db.relationship("User")
    Pool = db.relationship("Pool")

    @staticmethod
    def get_reservation(reservation_id):
        return Reservation.query.filter(Reservation.ID == reservation_id).first()

    def cancel(self):
        if self.Cancelled:
            print("Reservation " + self.ID + " is already cancelled")
            raise AttributeError

        self.Cancelled = True
        db.session.commit()

    def set_machine_count(self, machine_count):
        if machine_count <= self.MachineCount:
            self.MachineCount = machine_count
            db.session.commit()
        else:
            available_machines = self.Pool.available_machines(self.StartDate, self.EndDate)
            if machine_count - self.MachineCount > available_machines:
                raise ValueError("There are not enough available machines in given time frame")

    def __repr__(self):
        reservation_object = {
            "ID": self.ID,
            "PoolID": self.PoolID,
            "UserID": self.UserID,
            "StartDate": self.StartDate,
            "EndDate": self.EndDate,
            "MachineCount": self.MachineCount,
            "Cancelled": self.Cancelled
        }
        return json.dumps(reservation_object)


class Software(db.Model):
    __tablename__ = "Software"

    ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String)

    @staticmethod
    def get_software(software_id):
        return Software.query.filter(Software.ID == software_id).first()

    @staticmethod
    def get_software_by_name(name):
        return Software.query.filter(Software.Name == name).first()

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
