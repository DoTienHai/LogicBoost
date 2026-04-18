from pathlib import Path

base_dir = Path(__file__).resolve().parent
instance_dir = base_dir / "instance"
db_path = instance_dir / "logicboost.db"
file_uri = db_path.as_uri()
sqlite_uri = file_uri.replace("file://", "sqlite://")

print("Base dir:", base_dir)
print("DB path:", db_path)
print("File URI:", file_uri)
print("SQLite URI:", sqlite_uri)

# Also test config
from config import Config
print("\nConfig DB URI:", Config.SQLALCHEMY_DATABASE_URI)
