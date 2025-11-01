from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"

# 🔥 Firebase Initialization
cred = credentials.Certificate("serviceAccountKey.json")  # your Firebase service account key
firebase_admin.initialize_app(cred)
db = firestore.client()


# 🏠 Home Page
@app.route("/")
def home():
    events_ref = db.collection("events")
    events = [doc.to_dict() for doc in events_ref.stream()]
    user = session.get("role")
    return render_template("home.html", events=events, user=user)


# 👤 User Signup
@app.route("/user_signup", methods=["GET", "POST"])
def user_signup():
    if request.method == "POST":
        email = request.form["username"].lower()
        password = request.form["password"]

        # 🔎 Check if user already exists
        existing_user = db.collection("users").where("email", "==", email).get()
        if existing_user:
            return render_template("user_signup.html", error="An account with this email already exists!")

        # ✅ Add new user
        db.collection("users").add({
            "email": email,
            "password": password,
            "role": "user",
            "created_at": datetime.datetime.now()
        })
        return redirect(url_for("user_login"))

    return render_template("user_signup.html")


# 🔑 User Login
@app.route("/user_login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        email = request.form["username"].lower()
        password = request.form["password"]

        users = db.collection("users").where("email", "==", email).where("password", "==", password).get()
        if users:
            session["role"] = "user"
            session["email"] = email
            return redirect(url_for("home"))
        else:
            return render_template("user_login.html", error="Invalid email or password!")

    return render_template("user_login.html")


# 👩‍💼 Organizer/Admin Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["role"] = "admin"
            return redirect(url_for("admin"))
        elif username == "organizer" and password == "organizer123":
            session["role"] = "organizer"
            return redirect(url_for("organizer"))
        else:
            return render_template("login.html", error="Invalid credentials!")

    return render_template("login.html")


# 📊 Admin Dashboard
@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    # Total users (from Firestore)
    total_users = len(list(db.collection("users").stream()))

    # Total events
    total_events = len(list(db.collection("events").stream()))

    # Total attendees
    total_attendees = len(list(db.collection("attendees").stream()))

    return render_template(
        'admin.html',
        total_users=total_users,
        total_events=total_events,
        total_attendees=total_attendees
    )


# 🎤 Organizer Dashboard
@app.route('/organizer')
def organizer():
    user = session.get('user')
    if user not in ['organizer', 'admin']:
        return redirect(url_for('login'))

    # Fetch all events and attendees from Firestore
    events_ref = db.collection("events").stream()
    attendees_ref = db.collection("attendees").stream()

    # Create a lookup dictionary for event names
    event_lookup = {e.id: e.to_dict().get("name", "Unnamed Event") for e in events_ref}

    # Attach event names to attendees safely
    attendees = []
    for a in attendees_ref:
        data = a.to_dict()
        event_id = data.get("event_id")
        data["event_name"] = event_lookup.get(event_id, "Unknown Event")
        attendees.append(data)

    # Fetch events again for listing (since we consumed stream)
    events_ref = db.collection("events").stream()
    events = [{"id": e.id, **e.to_dict()} for e in events_ref]

    return render_template('organizer.html', attendees=attendees, events=events)


# ➕ Add Event
@app.route("/add_event", methods=["GET", "POST"])
def add_event():
    if session.get("role") not in ["organizer", "admin"]:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        date = request.form["date"]
        venue = request.form["venue"]

        db.collection("events").add({
            "name": name,
            "date": date,
            "venue": venue,
            "created_by": session.get("role"),
            "created_at": datetime.datetime.now()
        })
        return redirect(url_for("organizer"))

    return render_template("add_event.html")


# 🧾 Event Registration (User)
@app.route('/register', methods=['GET', 'POST'])
def register():
    events = [{"id": e.id, **e.to_dict()} for e in db.collection("events").stream()]

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        event_id = request.form.get('event_id')

        if not name or not email or not event_id:
            return render_template('register.html', events=events, error="All fields are required!")

        # Prevent duplicate registration
        existing = db.collection("attendees").where("email", "==", email).where("event_id", "==", event_id).stream()
        if any(existing):
            return render_template('register.html', events=events, error="You are already registered for this event!")

        # Save registration
        db.collection("attendees").add({
            "name": name,
            "email": email,
            "event_id": event_id,
            "registered_at": datetime.datetime.now()
        })

        # Only pass success on POST registration
        return render_template('register.html', events=events, success="You have successfully registered for the event!")

    # GET request → do not pass success or error
    return render_template('register.html', events=events)


@app.route('/export_attendees')
def export_attendees():
    if session.get('user') != 'admin':
        return redirect(url_for('login'))

    attendees = db.collection("attendees").stream()

    def generate_csv():
        output = "Name,Email,Event ID\n"
        for a in attendees:
            data = a.to_dict()
            output += f"{data['name']},{data['email']},{data['event_id']}\n"
        return output

    csv_data = generate_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=attendees.csv"}
    )


# 🚪 Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
