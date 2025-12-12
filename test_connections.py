import psycopg2
from pymongo import MongoClient

def test_postgresql():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="recruitgenie",
            user="recruitgenie_user",
            password="yourStrongPassword"   # Use the password you used while creating the user
        )
        print("✅ PostgreSQL connection successful!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL failed: {e}")
        return False

def test_mongodb():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client.recruitgenie
        db.test.insert_one({"test": "connection"})
        db.test.delete_many({"test": "connection"})
        print("✅ MongoDB connection successful!")
        return True
    except Exception as e:
        print(f"❌ MongoDB failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing database connections...")
    pg = test_postgresql()
    mongo = test_mongodb()
    if pg and mongo:
        print("🎉 All databases working!")
    else:
        print("⚠️ Some connections failed")



