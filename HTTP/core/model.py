import asyncio
from peewee import SqliteDatabase, Model, AutoField, CharField, DoesNotExist

class DBWrapper:
    def __init__(self, db_path):
        self.db = SqliteDatabase(db_path)
        self.db.connect()

        class BaseModel(Model):
            class Meta:
                database = self.db

        self.BaseModel = BaseModel
        self.models = {}

    def create_model(self, name, fields):
        attrs = {"__module__": __name__}
        attrs.update(fields)
        model_class = type(name, (self.BaseModel,), attrs)
        model_class.create_table()
        self.models[name] = model_class
        return model_class

    async def create(self, model_name, **data):
        model = self.models.get(model_name)
        if not model:
            raise ValueError(f"Model '{model_name}' not found")

        def sync_create():
            return model.create(**data)

        return await asyncio.to_thread(sync_create)

    async def get(self, model_name, **query):
        model = self.models.get(model_name)
        if not model:
            raise ValueError(f"Model '{model_name}' not found")

        def sync_get():
            try:
                return model.get(**query)
            except DoesNotExist:
                return None

        return await asyncio.to_thread(sync_get)

    async def update(self, model_name, query: dict, data: dict):
        model = self.models.get(model_name)
        if not model:
            raise ValueError(f"Model '{model_name}' not found")

        def sync_update():
            q = model.update(**data).where(*(getattr(model, k) == v for k, v in query.items()))
            return q.execute()

        return await asyncio.to_thread(sync_update)

    async def delete(self, model_name, **query):
        model = self.models.get(model_name)
        if not model:
            raise ValueError(f"Model '{model_name}' not found")

        def sync_delete():
            q = model.delete().where(*(getattr(model, k) == v for k, v in query.items()))
            return q.execute()

        return await asyncio.to_thread(sync_delete)

    async def all(self, model_name):
        model = self.models.get(model_name)
        if not model:
            raise ValueError(f"Model '{model_name}' not found")

        def sync_all():
            return list(model.select())

        return await asyncio.to_thread(sync_all)

    async def run_raw(self, sql, params=None):
        def sync_raw():
            cursor = self.db.execute_sql(sql, params or ())
            return cursor.fetchall()

        return await asyncio.to_thread(sync_raw)

    async def close(self):
        await asyncio.to_thread(self.db.close)
