import sqlite3 as sql3

def connect(folder):
  db = sql3.connect(folder + '\\base.db', check_same_thread=True)
  sql = db.cursor()
  # create(db, sql)
  return db, sql

def create(db, sql):
  sql.execute("""CREATE TABLE IF NOT EXISTS english (
      word TEXT,
      translate TEXT,
      sentence TEXT
    )""")

  db.commit()

  sql.execute("""CREATE TABLE IF NOT EXISTS texts (
    id INT,
    text TEXT
  )""")

  db.commit()

# db, sql = connect('Ö(183278535)')
# connect('Ö(183278535)')
# print('helo')