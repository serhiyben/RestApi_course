from locust import HttpUser, task, between


class LibraryUser(HttpUser):

    wait_time = between(1, 2)

    @task
    def get_public_books(self):
        """Емулюємо перегляд книг анонімним користувачем"""

        self.client.get("/books/public")
