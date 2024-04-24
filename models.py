
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class BaseModel:
    def __commit(self):
        from sqlalchemy.exc import IntegrityError

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    def delete(self):
        db.session.delete(self)
        self.__commit()

    def save(self):
        db.session.add(self)
        self.__commit()
        return self

    @classmethod
    def from_dict(cls, model_dict):
        return cls(**model_dict).save()

class File(db.Model, BaseModel):
    __tablename__ = "file"
    code = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(256))
    data = db.Column(db.LargeBinary)