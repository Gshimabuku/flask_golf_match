import os
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DB_COURSES_ID = os.getenv("NOTION_DB_COURSES_ID")
NOTION_DB_LAYOUTS_ID = os.getenv("NOTION_DB_LAYOUTS_ID")
NOTION_DB_HOLES_ID = os.getenv("NOTION_DB_HOLES_ID")
NOTION_DB_ROUNDS_ID = os.getenv("NOTION_DB_ROUNDS_ID")
NOTION_DB_SCORES_ID = os.getenv("NOTION_DB_SCORES_ID")
NOTION_DB_USERS_ID = os.getenv("NOTION_DB_USERS_ID")
