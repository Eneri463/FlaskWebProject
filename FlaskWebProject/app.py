from flask import Flask, request, jsonify
import sqlalchemy
from sqlalchemy import create_engine, text
from geopy.geocoders import Nominatim


app = Flask(__name__)
db = create_engine('postgresql://postgres:root@localhost/userdb')
geolocator = Nominatim(user_agent="app")


# получение координат по названию города
# название городов ожидаются на русском языке
def getLocation(name):
    
    location = geolocator.geocode(name, language="ru")
    
    if location:
        return location.latitude, location.longitude
    else:
        return False


@app.route('/')
@app.route('/home')
def index():

    print(getLocation("Лондон"))

    data = 'London, England'

    try:
        with db.connect() as conn:

            res = conn.execute(text("SELECT name, ST_Y(the_geom), ST_X(the_geom) \
                                    FROM cities WHERE name = :name;"),
                                    {"name": data})
            conn.commit()

            strinn = res.first()

            if strinn:
                return jsonify({'name': strinn[0], 'latitude': strinn[1], 
                                'longitude': strinn[2], 'message': "OK"}), 200

            else:
                return jsonify({'message': "Not Found"}), 404
    except:
        return jsonify({'message': "Internal Server Error"}), 500
        

# запрос на просмотр информации о городе
@app.route('/cities', methods=['GET'])
def getCity():
    
    try:
        
        data = request.json.get('name')

        with db.connect() as conn:
                
            res = conn.execute(text("SELECT name, ST_Y(the_geom), ST_X(the_geom) \
                                    FROM cities WHERE name = :name;"),
                            {"name": data})

            strinn = res.first()

            if strinn:
                return jsonify({'name': strinn[0], 'latitude': strinn[1], 'longitude': strinn[2], 'message': "OK"}), 200

            else:
                return jsonify({'message': "Not Found"}), 404
        
    except:
        return jsonify({'message': "Internal Server Error"}), 500
 

# запрос на добавление информации о городе
@app.route('/cities', methods=['POST'])
def postCity():
    
    try:
            
        data = request.json.get('name')
        
        with db.connect() as conn:
            res = conn.execute(text("SELECT name \
                                    FROM cities WHERE name = :name;"),
                                    {"name": data})

            strinn = res.first()

        if strinn:
            return jsonify({'message': "Already exists"}), 200

        else:
            
            res = getLocation(data)
            
            if res:
                latitude = res[0]
                longitude = res[1]

                with db.connect() as conn:

                    conn.execute(text("INSERT INTO cities (the_geom, name) \
                                      VALUES (ST_GeomFromText('POINT(:longitude :latitude)', 4326), :name);"),
                                      {"name": data, "latitude": latitude, "longitude": longitude})
                    conn.commit()
                    
                return jsonify({'message': "Created"}), 201
            else:
                return jsonify({'message': "This city does not exist"}), 400
    except:
        return jsonify({'message': "Internal Server Error"}), 500


# запрос на удаление информации о городе
@app.route('/cities', methods=['DELETE'])
def delCity():
    
    try:
        data = request.json.get('name')
        
        with db.connect() as conn:

            conn.execute(text("DELETE FROM cities \
                              WHERE name = :name"),
                              {"name": data})
            conn.commit()
                    
            return jsonify({'message': "OK"}), 200
        
    except:
        return jsonify({'message': "Internal Server Error"}), 500


 # запрос на поиск ближайшего города по координатам
@app.route('/nearCity', methods=['GET'])
def getNearCity():
    
    if request.method == "GET":
        
        data = request.json
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        try:
            with db.connect() as conn:
                res = conn.execute(text("SELECT name, ST_Y(the_geom), ST_X(the_geom), \
                                        MIN(ST_Distance_Sphere(the_geom, ST_GeomFromText('POINT(:p1 :p2)',4326))) \
                                        as dist FROM cities;"),
                                        {"p2": latitude, "p1": longitude})

                return jsonify({'city': res.first()[0], 'message': "OK"}), 200
        except:
            
            return jsonify({'message': "Internal Server Error"}), 500


if __name__ == '__main__':
    
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555

    # запускаем локальный сервер
    app.run(HOST, PORT)