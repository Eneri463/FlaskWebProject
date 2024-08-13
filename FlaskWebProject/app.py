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


# запрос на просмотр информации об одном городе
@app.route('/city', methods=['GET'])
def getCity():
    
    try:
        
        data = request.args.get('name')

        with db.connect() as conn:
                
            res = conn.execute(text("SELECT name, ST_Y(the_geom), ST_X(the_geom) \
                                    FROM cities WHERE name = :name;"),
                            {"name": data})

            strinn = res.first()

            if strinn:
                return jsonify({'name': strinn[0], 'latitude': strinn[1], 'longitude': strinn[2]}), 200
            else:
                return jsonify({'message': 'Not Found'}), 404
        
    except:
        return jsonify({'message': 'Something went wrong'}), 400
 

# запрос на добавление информации о городе
@app.route('/city', methods=['POST'])
def postCity():
    
    try:
            
        data = request.json.get('name')
            
        res = getLocation(data)
            
        if res:
            latitude = float(res[0])
            longitude = float(res[1])

            with db.connect() as conn:

                conn.execute(text("INSERT INTO cities (the_geom, name) \
                                    VALUES (ST_GeomFromText('POINT(:longitude :latitude)', 4326), :name);"),
                                    {"name": data, "latitude": latitude, "longitude": longitude})
                conn.commit()
                    
            return jsonify({'message': "Created"}), 201
        else:
            return jsonify({'message': "This city does not exist"}), 400
    except:
        return jsonify({'message': 'Something went wrong'}), 400


# запрос на удаление информации о городе
@app.route('/city', methods=['DELETE'])
def delCity():
    
    try:
        data = request.args.get('name')
        
        with db.connect() as conn:

            conn.execute(text("DELETE FROM cities \
                              WHERE name = :name"),
                              {"name": data})
            conn.commit()
                    
            return jsonify({'message': "OK"}), 200
        
    except:
        return jsonify({'message': 'Something went wrong'}), 400


# запрос на просмотр информации обо всех городах
@app.route('/cities', methods=['GET'])
def getCities():
    
    try:
        
        with db.connect() as conn:
                
            res = conn.execute(text("SELECT name, ST_Y(the_geom), ST_X(the_geom) \
                                    FROM cities;"))

            payload = []
            content = {}
            for result in res:
                content = {'name': result[0], 'latitude': result[1], 'longitude': result[2]}
                payload.append(content)
                content = {}

            return jsonify(payload), 200
        
    except:
        return jsonify({'message': 'Something went wrong'}), 400


 # запрос на поиск ближайших городов по координатам
@app.route('/nearestCities', methods=['GET'])
def getNearCity():
        
    try:
        
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))

        with db.connect() as conn:
            res = conn.execute(text("SELECT name, ST_Y(the_geom), ST_X(the_geom), ST_DistanceSphere(the_geom, \
                                    ST_GeomFromText('POINT(:p1 :p2)', 4326)) AS distance \
                                    FROM cities \
                                    ORDER BY distance \
                                    LIMIT 2;"),
                                    {"p2": latitude, "p1": longitude})

            payload = []
            content = {}
            for result in res:
                content = {'name': result[0], 'latitude': result[1], 'longitude': result[2]}
                payload.append(content)
                content = {}

            return jsonify(payload), 200
    except:
        return jsonify({'message': 'Something went wrong'}), 400


if __name__ == '__main__':
    
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555

    # запускаем локальный сервер
    app.run(HOST, 5005)