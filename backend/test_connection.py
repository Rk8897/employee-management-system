import pymysql

print("="*60)
print("Testing MySQL 9.4 Connection")
print("="*60)

try:
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="8897",   # 🔴 ADD THIS
        database="employee_db",
        port=3306
    )
    print("✅ SUCCESS: Connected to MySQL database")
    connection.close()

except Exception as e:
    print("❌ ERROR:", e)
