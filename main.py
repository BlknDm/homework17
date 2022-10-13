# импорт необходимых пакетов
from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship


#регистрация приложения и его конфиги
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 4}


#создание экземпляра базы данных
db = SQLAlchemy(app)


#формирование API REST
api = Api(app)


#формирование неймспейсов
movie_ns = api.namespace('movies')
genre_ns = api.namespace('genres')
director_ns = api.namespace('directors')


#создание класса Movie
class Movie(db.Model):
    __tablename__ = 'movie'
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(String(255))
    trailer = Column(String(255))
    rating = Column(Float)
    year = Column(Integer)
    genre_id = Column(Integer, ForeignKey("genre.id"))
    genre = relationship("Genre")
    director_id = Column(Integer, ForeignKey("director.id"))
    director = relationship("Director")


#создание класса Director
class Director(db.Model):
    __tablename__ = 'director'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))


#создание класса Genre
class Genre(db.Model):
    __tablename__ = 'genre'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))


#готовим схемы
class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    rating = fields.Float()
    year = fields.Int()
    genre = fields.Nested(GenreSchema, only=("name",))
    genre_id = fields.Int()
    director = fields.Pluck(field_name="name", nested=DirectorSchema)
    director_id = fields.Int()


#готовим сериализаторы для списков и элементов
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


#готовим реализацию методов для Movie(GET, POST)
@movie_ns.route("/")
class MoviesView(Resource):
    def get(self):
        """возвращает список всех фильмов и по параметрам"""
        all_movies = Movie.query

        director_id = request.args.get("director_id")
        page = request.args.get("page")

        if director_id:
            all_movies = all_movies.filter(Movie.director_id == director_id)

        genre_id = request.args.get("genre_id")
        if genre_id:
            all_movies = all_movies.filter(Movie.genre_id == genre_id)

        if page:
            all_movies = all_movies.paginate(int(page), 2).items

        return movies_schema.dump(all_movies)

    def post(self):
        data = request.json
        try:
            db.session.add(
                Movie(
                    **data
                )
            )
            db.session.commit()
            return "Данные добавлены", 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return e, 200

#готовим реализацию методов для Movie(GET, PUT, DELETE)
@movie_ns.route("/<int:mid>")
class MovieView(Resource):
    def get(self, mid):
        """возвращает подробную информацию о фильме"""
        one_movie = Movie.query.get(mid)
        return movie_schema.dump(one_movie)

    def put(self, mid):
        data = request.json
        try:
            db.session.query(Movie).filter(Movie.id == mid).update(
                data
            )
            db.session.commit()
            return "Данные обновлены", 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return e, 200


    def delete(self, mid):
        try:
            db.session.query(Movie).filter(Movie.id == mid).delete()
            db.session.commit()
            return "Данные удалены", 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return e, 200


#готовим реализацию методов для Director(GET, POST)
@director_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        """возвращает список всех режиссеров"""
        all_directors = Director.query
        return directors_schema.dump(all_directors)

    def post(self):
        data = request.json
        try:
            db.session.add(
                Director(
                    **data
                )
            )
            db.session.commit()
            return "Данные добавлены", 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return e, 200

#готовим реализацию методов для Director(GET, PUT, DELETE)
@director_ns.route("/<int:did>")
class DirectorView(Resource):
    def get(self, did):
        """возвращает подробную информацию о режиссере"""
        one_director = Director.query.get(did)
        return director_schema.dump(one_director)

    def put(self, did):
        data = request.json
        try:
            db.session.query(Director).filter(Director.id == did).update(
                data
            )
            db.session.commit()
            return "Данные обновлены", 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return e, 200


    def delete(self, did):
        try:
            db.session.query(Director).filter(Director.id == did).delete()
            db.session.commit()
            return "Данные удалены", 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return e, 200



#готовим реализацию методов для Genre(GET, POST)
@genre_ns.route("/")
class GenresView(Resource):
    def get(self):
        """возвращает список всех жанров"""
        all_genres = Genre.query
        return genres_schema.dump(all_genres)

    def post(self):
        data = request.json
        try:
            db.session.add(
                Director(
                    **data
                )
            )
            db.session.commit()
            return "Данные добавлены", 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return e, 200

#готовим реализацию методов для Genre(GET, PUT, DELETE)
@movie_ns.route("/<int:gid>")
class MovieView(Resource):
    def get(self, gid):
        """возвращает жанр"""
        one_genre = Genre.query.get(gid)
        return genre_schema.dump(one_genre)

    def put(self, gid):
        data = request.json
        try:
            db.session.query(Genre).filter(Genre.id == gid).update(
                data
            )
            db.session.commit()
            return "Данные обновлены", 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return e, 200


    def delete(self, gid):
        try:
            db.session.query(Genre).filter(Genre.id == gid).delete()
            db.session.commit()
            return "Данные удалены", 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return e, 200


if __name__ == '__main__':
    app.run(port=20500)
