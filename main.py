from pymongo import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://user:password@cluster0.rfwim81.mongodb.net/?appName=Cluster0"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.book

result_many = db.my_cats.insert_many(
    [
        {
            "name" : "Grace",
            "age" : 7,
            "features" : ["муркає", "любить гратися"],
        },
        {
            "name" : "Вася",
            "age" : 5,
            "features" : ["колобок", "любить поїсти"],
        },
        {
            "name" : "Мурчик",
            "age" : 10,
            "features" : ["пухнастик", "любить спати"],
        },
    ]
)

class NotFoundDocument(ValueError):
    pass

class NotDigitalError(ValueError):
    pass

# Декоратор для ловіння помилок
def catch_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotFoundDocument:
            print("Provided name of the cat is not existent")
        except NotDigitalError:
            print("Please provide age as a digit")
        except Exception as e:
            print(f"Сталася непередбачувана помилка: {e}")
    return inner

#Функція для виведення всіх документів (котів)
def print_results():
    results = db.my_cats.find({})
    for result in results:
        print(result)

#Функція для виведення конкретного кота (за ім'ям)
@catch_error
def print_some_cat(name):
    result = db.my_cats.find_one({"name" : name})
    if result is not None:
        print(result)
    else: 
        raise NotFoundDocument

#Функція для оновлення віку для конкретного кота
@catch_error
def update_some_cat(name, age):
    if age.isdigit():
        db.my_cats.update_one({"name" : name}, {"$set": {"age": age}})
        print_some_cat(name)
    else:
        raise NotDigitalError

#Функція для додавання нових особливостей до кота
@catch_error
def add_feature(name, *args):
    for arg in args:
        db.my_cats.update_one({"name": name}, {"$push": {"features": arg}})
    print_some_cat(name)

#Функція для видалення конкретного кота із бази даних
@catch_error
def delete_one(name):
    result = db.my_cats.find_one({"name" : name})
    if result is not None:
        db.my_cats.delete_one({"name": name})
    else:
        raise NotFoundDocument

#Функція для видалення всіх документів
@catch_error
def delete_all():
    db.my_cats.delete_many({})


if __name__ == "__main__":
    print_results()
    print_some_cat("Grace")
    update_some_cat("Grace", 3)
    add_feature("Вася", "ходить гулять", "муркає")
    delete_one("Мурчик")
    print_results()
    delete_all()
    
