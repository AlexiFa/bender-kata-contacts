import sys
import sqlite3
from pathlib import Path
from datetime import datetime


class Contacts:
    def __init__(self, db_path):
        self.db_path = db_path
        if not db_path.exists():
            print("Migrating db")
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE contacts(
                  id INTEGER PRIMARY KEY,
                  name TEXT NOT NULL,
                  email TEXT NOT NULL
                )
              """
            )
            connection.commit()
            cursor.execute(
                """
                CREATE INDEX contacts_email ON contacts(email);
              """
            )
            connection.commit()
            cursor.close()
            connection.close()
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row

    def insert_contacts(self, contacts):
        print("Inserting contacts ...")
        # TODO
        cursor = self.connection.cursor()
        start = datetime.now()     
        cursor.executemany(
            """
            INSERT INTO contacts(name, email)
            VALUES (?, ?)
            """,
            contacts,
        )
        self.connection.commit()
        end = datetime.now()

        elapsed = end - start
        # print time in seconds
        print("insert took", elapsed.total_seconds() * 1000, "ms")
        cursor.close()


    def get_name_for_email(self, email):
        print("Looking for email", email)
        cursor = self.connection.cursor()
        start = datetime.now()
        cursor.execute(
            """
            SELECT * FROM contacts
            WHERE email = ?
            """,
            (email,),
        )
        row = cursor.fetchone()
        end = datetime.now()

        elapsed = end - start
        print("query took", elapsed.total_seconds() * 1000, "ms")
        if row:
            name = row["name"]
            print(f"Found name: '{name}'")
            cursor.close()
            return name
        else:
            print("Not found")
            cursor.close()


def yield_contacts(num_contacts):
    for i in range(num_contacts):
        yield (f"name-{i+1}", f"email-{i+1}@domain.tld")


def main():
    num_contacts = int(sys.argv[1])
    db_path = Path("contacts.sqlite3")
    contacts = Contacts(db_path)
    contacts.insert_contacts(yield_contacts(num_contacts))
    charlie = contacts.get_name_for_email(f"email-{num_contacts}@domain.tld")
    contacts.connection.close()


if __name__ == "__main__":
    main()
    # remove file after execution
    Path("contacts.sqlite3").unlink()
