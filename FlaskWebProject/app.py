from flask import Flask, request, jsonify
import sqlalchemy
from sqlalchemy import create_engine, text


app = Flask(__name__)
db = create_engine('postgresql://postgres:root@localhost/userdb')


@app.route('/')
@app.route('/home')
def index():

    data = 'London, England'

    try:
        with db.connect() as conn:

            res = conn.execute(text("SELECT name, ST_X(the_geom), ST_Y(the_geom) FROM cities WHERE name = :name;"),
                            {"name": data})
            conn.commit()

            strinn = res.first()

            if strinn:
                return jsonify({'name': strinn[0], 'latitude': strinn[1], 'longitude': strinn[2]}), 201

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
                
            res = conn.execute(text("SELECT name, ST_X(the_geom), ST_Y(the_geom) FROM cities WHERE name = :name;"),
                            {"name": data})

            strinn = res.first()

            if strinn:
                return jsonify({'name': strinn[0], 'latitude': strinn[1], 'longitude': strinn[2]}), 201

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
            res = conn.execute(text("SELECT name FROM cities WHERE name = :name;"),
                            {"name": data})

            strinn = res.first()

        if strinn:
            return jsonify({'message': "Already exists"}), 200

        else:
    
            latitude = -0.1257
            longitude = 51.508

            with db.connect() as conn:

                conn.execute(text("INSERT INTO cities (the_geom, name) VALUES (ST_GeomFromText('POINT(:latitude :longitude)', 4326), :name);"),
                                {"name": data, "latitude": latitude, "longitude": longitude,})
                conn.commit()
                    
            return jsonify({'message': "Created"}), 201
   
    except:
        return jsonify({'message': "Internal Server Error"}), 500


# запрос на удаление информации о городе
@app.route('/cities', methods=['DELETE'])
def delCity():
    
    try:
        data = request.json
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        return "User page: "
        
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
                res = conn.execute(text("SELECT name, MIN(ST_Distance_Sphere(the_geom, ST_GeomFromText('POINT(:p1 :p2)',4326))) as dist FROM cities;"),
                             {"p1": latitude, "p2": longitude})
                conn.commit()

                return jsonify({'city': res.first()[0]}), 201
        except:
            
            return jsonify({'message': "Sourse create"}), 500


if __name__ == '__main__':
    
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555

    # запускаем локальный сервер
    app.run(HOST, PORT)