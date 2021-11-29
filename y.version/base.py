import sqlite3 as sql3

db = sql3.connect('base.db', check_same_thread=False)
cursor = db.cursor()

cursor.execute(f"INSERT INTO english VALUES (?, ?, ?)", ('he', 'он', 'he is sick'))
db.commit()


cursor.execute("SELECT translate FROM english WHERE word = 'het'")
data = cursor.fetchall()
if not data:
    print('None')