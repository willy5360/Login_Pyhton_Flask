from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return f' email:{self.email}, password: {self.password}'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
        }

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def get_by_email(cls, email):
        member = cls.query.filter_by(email=email).one_or_none()
        return member

    @classmethod
    def get_all(cls):
        members = cls.query.all()
        return members