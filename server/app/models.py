from peewee import *
from playhouse.postgres_ext import *
# docker run --name postgres -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_DB=postgres postgres:13.3

#connection with database

conn = PostgresqlExtDatabase(
            host="localhost",
            database="postgres",
            user="postgres",
            port="5432",
            password="mysecretpassword")

#initialization tables

class BaseModel(Model):
    class Meta:
        database = conn

class Type(BaseModel):
    id = AutoField(column_name='id')
    name = CharField(column_name='name')
    class Meta:
        table_name = 'types'

class UnitMeasure(BaseModel):
    id = AutoField(column_name='id')
    name = CharField(column_name='name')
    class Meta:
        table_name = 'unitmeasures'

class Ingredient(BaseModel):
    id = AutoField(column_name='id')
    name = CharField(column_name='name')
    typeid = IntegerField(column_name='typeid')
    unitmeasureid = IntegerField(column_name='unitmeasureid')
    class Meta:
        table_name = 'ingredients'

class Cuisine(BaseModel):
    id = AutoField(column_name='id')
    name = CharField(column_name='name')
    class Meta:
        table_name = 'cuisines'

class Recipe(BaseModel):
    id = AutoField(column_name='id')
    name = CharField(column_name='name')
    inf = CharField(column_name='information', null=True)
    cuisineid = IntegerField(column_name='cuisineid')
    countsteps = IntegerField(column_name='countsteps')
    steps = ArrayField(column_name='steps')
    countlikes = IntegerField(column_name='countlikes')
    class Meta:
        table_name = 'recipes'

class User(BaseModel):
    id = AutoField(column_name='id')
    name = CharField(column_name='username')
    password = CharField(column_name='userpassword')
    class Meta:
        table_name = 'users'

class StrFridge(BaseModel):
    userid = AutoField(column_name='userid')
    ingredientsid = ArrayField(column_name='ingredientsid')
    class Meta:
        table_name = 'matrixfridge'

class StrIngredient(BaseModel):
    recipeid = AutoField(column_name='recipeid')
    ingredientsid = ArrayField(column_name='ingredientsid')
    class Meta:
        table_name = 'matrixingredients'

class StrFavorite(BaseModel):
    userid = AutoField(column_name='userid')
    recipesid = ArrayField(column_name='recipesid')
    class Meta:
        table_name = 'matrixfavorite'

#query by name of the table

def object(table):
    if table == "type":
        return Type.select()
    elif table == "unitmeasure":
        return UnitMeasure.select()
    elif table == "ingredient":
        return Ingredient.select()
    elif table == "cuisine":
        return Cuisine.select()
    elif table == "recipe":
        return Recipe.select()
    elif table == "user":
        return User.select()

#count of rows in the table

def cnt(table):
    query = object(table)
    table_selected = query.dicts().execute()
    cnt = 0
    for value in table_selected:            # {"id" = 1, "name" = "admin", "password" = "adminadmin"}
        cnt += 1
    return cnt

#from table to matrix

def fridge_to_matrix():
    query = StrFridge.select()
    str_selected = query.dicts().execute()
    matrix = [0] * cnt("user")
    for str in str_selected:
        matrix[str["userid"] - 1] = str["ingredientsid"]  # id start with 1; index start with 0
    return matrix

def ingredient_to_matrix():
    query = StrIngredient.select()
    str_selected = query.dicts().execute()
    matrix = [0] * cnt("recipe")
    for str in str_selected:
        matrix[str["recipeid"] - 1] = str["ingredientsid"]  # id start with 1; index start with 0
    return matrix

def favorite_to_matrix():
    query = StrFavorite.select()
    str_selected = query.dicts().execute()
    matrix = [0]*cnt("user")
    for str in str_selected:      # {"userid" : 1, "recipesid" :}
        matrix[str["userid"]-1] = str["recipesid"]   #id start with 1; index start with 0
    return matrix


def new_user():
    StrFridge.create(ingredientsid = [0] * cnt("ingredient"))
    StrFavorite.create(recipesid = [0] * cnt("recipe"))
    return 0

def new_recipe(data): # data = "cnt_id;id;cnt;id;cnt;..."
    input = data.split(";")   # ["7", "1", "10", ...]
    cnt_id = int(input.pop(0))
    new = [0]*cnt("ingredient")  # [0, ...]
    for i in range(cnt_id):
        new[int(input[i*2])-1] = int(input[i*2+1])
    StrIngredient.create(ingredientsid = new)
    query = StrFavorite.select()
    str_selected = query.dicts().execute()
    for item in str_selected:
        record = StrFavorite.get(StrFavorite.userid==item["userid"])
        record.recipesid.append(0)
        record.save()
    return 0

def new_ingredient():
    query = StrIngredient.select()
    str_selected = query.dicts().execute()
    for item in str_selected:
        record = StrIngredient.get(StrIngredient.recipeid == item["recipeid"])
        record.ingredientsid.append(0)
        record.save()
    query = StrFridge.select()
    str_selected = query.dicts().execute()
    for item in str_selected:
        record = StrFridge.get(StrFridge.userid == item["userid"])
        record.ingredientsid.append(0)
        record.save()
    return 0

def search_name(table, data):  # data = "name"
    query = object(table)
    table_selected = query.dicts().execute()
    for value in table_selected:
        if value["name"] == data:
            return value
    return -1
def search_id(table, data):  #data = int id
    query = object(table)
    table_selected = query.dicts().execute()
    for value in table_selected:
        if value["id"] == data:
            return value
    return -1

def search_substring(table, data):  # data = "name"
    query = object(table)
    user_selected = query.dicts().execute()
    output = []
    for user in user_selected:
        if data in  user["name"]:
            output.append(user)
    if output != []:
        return output
    return -1



#def new_user_name(data): # {"name" = "Mila", "password" = }

#print(Recipe.get(Recipe.id == 1))



#print(favorite_to_matrix())

#user = User.get(User.id == 1)
#print(user.name, user.password)

#request = {"name" : "Mila", "password" : "ilikekittys", "replay" : "ilikekittys"}
#User.create(id = 3, name = request["name"], password = request["password"])    #auto increment???????
#user = User.get(User.id == 3)
#user.save()

#user = User.get(User.id == 3)
#print(user)


