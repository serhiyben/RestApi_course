from flask import Flask, request
from flask_restful import Api, Resource
from flasgger import Swagger
from database import books_collection
from bson.objectid import ObjectId

app = Flask(__name__)
api = Api(app)

# Налаштування Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"  # Шлях до Swagger UI
}
swagger = Swagger(app, config=swagger_config)

class BookListResource(Resource):
    def get(self):
        """
        Отримати список всіх книг
        ---
        tags:
          - Books
        responses:
          200:
            description: Успішне отримання списку книг
        """
        books = []
        for book in books_collection.find():
            book['_id'] = str(book['_id']) # Конвертуємо ObjectId в рядок
            books.append(book)
        return books, 200  # <--- Просто повертаємо список

    def post(self):
        """
        Додати нову книгу
        ---
        tags:
          - Books
        parameters:
          - in: body
            name: body
            schema:
              type: object
              required:
                - title
                - author
              properties:
                title:
                  type: string
                  example: "Dune"
                author:
                  type: string
                  example: "Frank Herbert"
                year:
                  type: integer
                  example: 1965
        responses:
          201:
            description: Книгу успішно створено
        """
        data = request.get_json()
        result = books_collection.insert_one(data)
        
        new_book = books_collection.find_one({"_id": result.inserted_id})
        new_book['_id'] = str(new_book['_id'])
        return new_book, 201  # <--- Просто повертаємо словник

class BookResource(Resource):
    def get(self, book_id):
        """
        Отримати книгу за ID
        ---
        tags:
          - Books
        parameters:
          - in: path
            name: book_id
            required: true
            type: string
        responses:
          200:
            description: Дані книги
          404:
            description: Книгу не знайдено
        """
        try:
            book = books_collection.find_one({"_id": ObjectId(book_id)})
            if book:
                book['_id'] = str(book['_id'])
                return book, 200  # <--- Просто повертаємо словник
            return {"message": "Book not found"}, 404
        except Exception:
            return {"message": "Invalid book ID format"}, 400

    def delete(self, book_id):
        """
        Видалити книгу
        ---
        tags:
          - Books
        parameters:
          - in: path
            name: book_id
            required: true
            type: string
        responses:
          204:
            description: Книгу успішно видалено
          404:
            description: Книгу не знайдено
        """
        try:
            result = books_collection.delete_one({"_id": ObjectId(book_id)})
            if result.deleted_count == 1:
                return '', 204
            return {"message": "Book not found"}, 404
        except Exception:
            return {"message": "Invalid book ID format"}, 400

api.add_resource(BookListResource, '/books')
api.add_resource(BookResource, '/books/<string:book_id>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)