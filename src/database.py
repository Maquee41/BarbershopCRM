from peewee import *

db = MySQLDatabase("barbershopdb", host="localhost", port=3306, user="root", passwd="Tvg120181")


class BaseModel(Model):
    class Meta:
        database = db


class Clients(BaseModel):
    full_name = CharField()
    phone = CharField(max_length=15, unique=True)


class Service(BaseModel):
    item = CharField()
    price = CharField()


class History(BaseModel):
    client_id = ForeignKeyField(Clients, backref='clients')
    item = CharField()
    price = CharField()
    datetime = DateTimeField()
    feedback = IntegerField()


def create_client(full_name, phone):
    try:
        row = Clients(
            full_name=full_name,
            phone=phone
        )
        row.save()
        return 1
    except Exception as ex:
        return ex


def create_service(item, price):
    try:
        row = Service(
            item=item,
            price=price
        )
        row.save()
        return 1
    except Exception as ex:
        return ex


def create_history_item(client_name, item, datetime, feedback) -> int | str:
    try:
        client_id = get_client_id(client_name)
        price = get_service_price(item)
        row = History(
            client_id=client_id,
            item=item,
            price=price,
            datetime=datetime,
            feedback=feedback
        )
        row.save()
        return 1
    except Exception as ex:
        return str(ex)


def get_client_id(full_name: str) -> int | str:
    try:
        client_id = Clients.get(Clients.full_name == full_name).id
        return client_id
    except Exception as ex:
        return str(ex)


def get_service_price(item: str) -> int | str:
    try:
        price = Service.get(Service.item == item).price
        return price
    except Exception as ex:
        return str(ex)


def select_all_clients() -> list:
    try:
        return list(Clients.select().dicts())
    except Exception as ex:
        return [str(ex)]


def select_all_services() -> list:
    try:
        return list(Service.select().dicts())
    except Exception as ex:
        return [str(ex)]


def select_full_history():
    try:
        # return list(History.select().dicts())
        return list(History.select(History, Clients).join(Clients).dicts())
    except Exception as ex:
        return [str(ex)]


def get_all_service_items() -> list:
    try:
        return [i.item for i in Service.select(Service.item)]
    except Exception as ex:
        return list(str(ex))


def get_all_clients() -> list:
    try:
        return [i.full_name for i in Clients.select(Clients.full_name)]
    except Exception as ex:
        return list(str(ex))


def get_all_client_history(client_id: int) -> list:
    try:
        data = History.select().where(History.client_id == client_id).dicts()
        return data
    except Exception as ex:
        return [str(ex)]


def get_client_info(client_id: int) -> dict:
    try:
        data = Clients.select().where(Clients.id == client_id).get()
        return {'id': data.id, 'full_name': data.full_name, 'phone': data.phone}
    except Exception as ex:
        return {'error': str(ex)}


def get_history_item(history_id: int) -> dict:
    try:
        data = History.select(History, Clients).where(History.id == history_id).join(Clients).get()
        return {'id': data.id, 'client_name': data.client_id.full_name, 'client_phone': data.client_id.phone,
                'item': data.item, 'price': data.price, 'datetime': data.datetime, 'feedback': data.feedback}
    except Exception as ex:
        return {'error': str(ex)}


def get_service_item(service_id: int) -> dict:
    try:
        data = Service.select().where(Service.id == service_id).get()
        return {'id': data.id, 'item': data.item, 'price': data.price}
    except Exception as ex:
        return {'error': str(ex)}


def edit_history_item(item_id: int, item: str, price: str, datetime, feedback: int) -> str:
    try:
        History.update(
            item=item,
            price=price,
            datetime=datetime,
            feedback=feedback
        ).where(History.id == item_id).execute()
        return 'update'
    except Exception as ex:
        return str(ex)


def edit_service_item(item_id: int, item: str, price: str) -> str:
    try:
        Service.update(
            item=item,
            price=price
        ).where(Service.id == item_id).execute()
        return 'update'
    except Exception as ex:
        return str(ex)


def edit_client_item(user_id: int, full_name: str, phone: str) -> str:
    try:
        Clients.update(
            full_name=full_name,
            phone=phone
        ).where(Clients.id == user_id).execute()
        return 'updated'
    except Exception as ex:
        return str(ex)


def delete_history_item(item_id: int) -> str:
    try:
        History.delete_by_id(item_id)
        return 'delete'
    except Exception as ex:
        return str(ex)


def delete_service_item(item_id: int) -> str:
    try:
        Service.delete_by_id(item_id)
        return 'delete'
    except Exception as ex:
        return str(ex)


def create_db():
    db.connect()
    db.create_tables([Clients, Service, History])


def disconnect_db():
    db.close()


def main_db():
    create_db()


main_db()
