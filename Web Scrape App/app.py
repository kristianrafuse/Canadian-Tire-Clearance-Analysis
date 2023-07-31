import time
import math 
import pandas as pd
from splinter import Browser
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import re

from flask import Flask, jsonify, render_template, request
from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

app = Flask(__name__)

# Connection details
username = os.environ.get('DB_USERNAME')
password = os.environ.get('DB_PASSWORD')
host = os.environ.get('DB_HOST')
database = os.environ.get('DB_NAME')

# Create the database URL
url = f'postgresql://{username}:{password}@{host}/{database}'

# Create the engine
engine = create_engine(url)

# Create a base class for declarative models
Base = declarative_base()

# Create the table in the database
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

@app.route("/")
def welcome():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()