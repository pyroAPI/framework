from core.model import DBWrapper
from peewee import AutoField, CharField


db = DBWrapper("users.db")

User = db.create_model("User", {
    "id": AutoField(),
    "name": CharField(),
    "email": CharField()
})