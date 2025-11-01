# 🎟️ Event Management System

## 📖 Overview
The **Event Management System** is a Flask-based web application that enables organizers to manage events, track attendees, and handle registrations efficiently. It uses **Firebase Firestore** as the backend database for real-time data storage and retrieval.

This project provides an easy-to-use admin dashboard for managing events and attendees, along with secure authentication and organized data handling.

---

## ⚙️ Features
- 🔐 **Admin Login & Session Management** – Secure session-based login for admins or organizers.  
- 📅 **Event Management** – Add, edit, update, and delete events dynamically.  
- 👥 **Attendee Management** – Store and view attendee details for each event in Firestore.  
- 📊 **Dashboard Overview** – Admin dashboard to view all upcoming events and attendees at a glance.  
- ☁️ **Firebase Integration** – Firestore is used as the NoSQL database for fast and scalable data storage.  

---

## 🧰 Tech Stack
- **Frontend:** HTML, CSS, Jinja Templates  
- **Backend:** Flask (Python)  
- **Database:** Firebase Firestore  
- **Authentication:** Flask Sessions  
- **Cloud Platform:** Google Firebase  

---

## 🗂️ Folder Structure
EventManagementSystem/
│
├── static/ # CSS, JS, and images
├── templates/ # HTML templates (home.html, dashboard.html, etc.)
├── app.py # Main Flask application
├── serviceAccountKey.json # Firebase credentials (NOT included in repo)
└── requirements.txt # Python dependencies
