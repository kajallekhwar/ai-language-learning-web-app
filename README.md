# AI Language Learning Web App

A Flask-based AI-powered web application designed to enhance interactive and adaptive language learning.

## Features

- User Authentication System
- Interactive Quizzes
- Speech Recognition Integration
- Adaptive Difficulty Adjustment
- Personalized Flashcards
- SQLite Database Integration

## Tech Stack

- Python
- Flask
- HTML
- CSS
- JavaScript
- SQLite
- REST APIs

## Project Structure

ai-language-learning-web-app/
│
├── app.py
├── requirements.txt
├── schema.sql
├── static/
├── templates/

## Database Setup

Initialize the database using:

sqlite3 app.db < schema.sql

## Run Locally

pip install -r requirements.txt
python app.py

Then open:
http://127.0.0.1:5000/
