________________________________________________________________________________________________________________________________________________________________________________
ПОДДЕРЖИВАЕМЫЕ ЗАПРОСЫ
________________________________________________________________________________________________________________________________________________________________________________

1) GET '\city'       - возвращает информацию о конкретном городе

    в качестве параметров необходимо передать name; пример:
    http://localhost:5005/city?name=Новосибирск

2) DEL '\city'       - удаляет информацию о конкретном городе

    в качестве параметров необходимо передать name;
   
3) POST '\city'       - добавляет информацию о конкретном городе

    требует в body json вида:
   {
     "name": "Название города"
   }

5) GET '\cities'      - возвращает информацию обо всех городах в базе

   не требует параметров

5) GET '\nearestСities'      - возвращает информацию о двух ближайших городах

    в качестве параметров необходимо передать longitude (долгота) и latitude (широта); пример:
    http://localhost:5005/nearestCities?longitude=92.872586&latitude=56.0091173
    
________________________________________________________________________________________________________________________________________________________________________________
КАК ЗАПУСТИТЬ
________________________________________________________________________________________________________________________________________________________________________________
В качестве БД используется postgreSQL с установленным расширением PostGIS (https://postgis.net/).
Для того, чтобы программа работала, необходимо: 

1) создать БД
2) в базе даных выполнить следующий код:
   
   CREATE EXTENSION postgis;
   CREATE TABLE cities
   (
     id serial primary key,
     name varchar(50) NOT NULL UNIQUE,
     the_geom geometry(POINT,4326) NOT NULL
   );

3) чтобы запустить приложение, используйте файл "app.py"
  
