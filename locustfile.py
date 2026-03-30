from locust import HttpUser, task, between

class LibraryProfessionalUser(HttpUser):
    # Кожен бот чекає від 1 до 3 секунд між діями
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        """Виконується один раз для кожного бота при 'народженні'"""
        
        response = self.client.post("/token", data={
            "username": "test", 
            "password": "123456"
        }, name="00_Login_Action")
        
        # Перевіряємо, чи все ок, і забираємо токен
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            print(f"Login failed: {response.status_code}")

    @task(10)
    def view_public_books(self):
        """Публічне читання (найлегше завдання)"""
        self.client.get("/books/public", name="01_GET_Public_Books")

    @task(5)
    def view_private_catalog(self):
        """Авторизоване читання (перевірка JWT)"""
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.get("/books/", headers=headers, name="02_GET_Private_Books_JWT")

    @task(1)
    def create_book(self):
        """Запис у базу даних (найважче завдання)"""
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.post("/books/", headers=headers, json={
                "title": f"Stress Test Book {self.token[:5]}",
                "author": "Locust Bot",
                "description": "Load testing record",
                "year": 2026
            }, name="03_POST_Create_Book_Write")