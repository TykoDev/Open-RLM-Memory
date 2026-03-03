from app.core.config import settings


def check_imports():
    print(f"Project Name: {settings.PROJECT_NAME}")
    print(f"DB Type: {settings.DB_TYPE}")
    print("Imports successful")

if __name__ == "__main__":
    check_imports()
