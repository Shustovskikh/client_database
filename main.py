import psycopg2

# 1. Функция, создающая структуру БД (таблицы).
def create_db():
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Clients(
            id SERIAL PRIMARY KEY, 
            name VARCHAR(40) NOT NULL,
            lastname VARCHAR(40) NOT NULL,
            email VARCHAR(40) UNIQUE);
            """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Telephone_numbers(
            id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE, 
            number VARCHAR(20) NOT NULL UNIQUE);
            """)
        conn.commit()

# Функция удаляющая БД
def delete_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
		DROP TABLE IF EXISTS Clients, Telephone_numbers CASCADE;
		""")
    conn.commit()

# 2. Функция, позволяющая добавить нового клиента.
def add_client(conn, name, lastname, email, number=None):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO Clients(name, lastname, email) 
        VALUES(%s, %s, %s)
        RETURNING id, name, lastname, email;
        """, (name, lastname, email))
        new_client = cur.fetchone()
    if number is not None:
        cur.execute("""
        INSERT INTO Telephone_numbers(client_id, number) 
        VALUES(%s, %s) RETURNING client_id;
        """, (new_client[0], number))
        cur.fetchone()
    conn.commit()

# 3. Функция, позволяющая добавить телефон для существующего клиента.
def add_number(conn, client_id, number):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO Telephone_numbers(number, client_id)
        VALUES(%s, (SELECT id FROM Clients
        WHERE name=%s and lastname=%s and email=%s));
        """, (number, client_id))
    conn.commit()

# 4. Функция, позволяющая изменить данные о клиенте.
def change_info(conn, id, name=None, lastname=None, email=None, number=None):
    if name is not None:
        with conn.cursor() as cur:
            cur.execute("""
            UPDATE Clients SET name = %s
            WHERE id = %s RETURNING id;
            """, (name, id))
    if lastname is None:
        with conn.cursor() as cur:
            cur.execute("""
            UPDATE Clients SET lastname = %s
            WHERE id = %s RETURNING id;
            """, (lastname, id))
    if email is None:
        with conn.cursor() as cur:
            cur.execute("""
            UPDATE clients SET email = %s
            WHERE id = %s RETURNING id;
            """, (email, id))
    if number is not None:
        with conn.cursor() as cur:
            cur.execute("""
            UPDATE Telephone_numbers SET number=%s
            WHERE id = %s RETURNING id;
            """, (number, id))
    conn.commit()

# 5. Функция, позволяющая удалить телефон для существующего клиента.
def delete_num(conn, client_id, number):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM Telephone_numbers
        WHERE client_id = (SELECT id FROM Clients
        WHERE name=%s and lastname=%s and email=%s);
        """, (client_id, number))
        conn.commit()

# 6. Функция, позволяющая удалить существующего клиента.
def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM clients
		WHERE id = %s;
		""", (client_id,))
    conn.commit()

# 7. Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону.
def search_client(conn, name=None, lastname=None, email=None, number=None):
    with conn.cursor() as cur:
        if number is not None:
            cur.execute("""
            SELECT c.id, c.name, c.lastname, c.email, c.number FROM Clients c
            LEFT JOIN numbers c ON c.id = n.client_id
            WHERE c.name LIKE %s AND c.lastname LiKE %s
            AND c.email LIKE %s; 
            """, (name, lastname, email))
        else:
            cur.execute("""
            SELECT c.id, c.name, c.lastname, c.email, c.nuber FROM Clients c
            LEFT JOIN numbers c ON c.id = n.client_id
            WHERE c.name LIKE %s AND c.lastname LIKE %s
            AND c.email LIKE %s AND c.number LIKE %s;
            """, (name, lastname, email, number))
        return cur.fetchall()

if __name__ == "__main__":
    with psycopg2.connect(database='clients_db', user='postgres', password='0000000') as conn:
        # Удаление БД
        delete_db(conn)
        print("БД удалена")
        # 1. Создание БД
        create_db(conn)
        print("БД создана")
        # 2. Добавить 3 клиента
        print("Клиент id: ",
              add_client(conn, "Иван_1", "Иванов_1", "ivan_1@mail.ru"))
        print("Клиент id: ",
            add_client(conn, "Иван_2", "Иванов_2", "ivan_2@mail.ru"))
        print("Клиент id: ",
            add_client(conn, "Иван_3", "Иванов_3", "ivan_3@mail.ru"))
        print("Данные о клиентах")
        # 3. Добавить телефон. номер клиента
        print("Номер добавлен id: ",
              add_number(conn, 1, 11111111111))
        print("Номер добавлен id: ",
              add_number(conn, 2, 22222222222))
        print("Номер добавлен id: ",
              add_number(conn, 3, 33333333333))
        print("Данные о клиентах")
        # 4. Изменить данные клиента (имя, фамилию, email)
        print("Изменить данные клиента id: ",
            change_info(conn, 1, name="Петр_1"),
            change_info(conn, 2, lastname="Петров_2"),
            change_info(conn, 3, email="petr_3@mail.ru"))
        # 5. Удалить телефон. номер клиента
        print("Номер удален: ",
            delete_num(conn, "3", "000000000000"))
        print("Данные о клиентах")
        # 6. Удалить клиента
        print("Клиент удален id: ",
            delete_client(conn, 3))
        # 7. Найти клиента по его данным (имени, фамилии, email)
        print("Найден клиент по фамилии: ",
            search_client(conn, name="Иван_2"))
        print("Найден клиент по фамилии: ",
            search_client(conn, lastname="Иванов_1"))
        print("Найден клиент по email: ",
            search_client(conn, email="ivan_3@mail.ru"))
        print("Найден клиент по телеф. номеру: ",
            search_client(conn, number="44444444444"))