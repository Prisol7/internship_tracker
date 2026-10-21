#!/usr/bin/env python3
# internship tracker bc my spreadsheet was getting out of hand lol
# uses sqlite so no mysql server needed

import sqlite3
import csv
from datetime import datetime
from pathlib import Path
import os
import sys

# keep the db and stuff next to the script so it dosent matter where u run it from
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "internship_tracker.db"
EXPORT_DIR = BASE_DIR / "exports"
ARCHIVE_DIR = BASE_DIR / "archive"

STATUSES = [
    "Applied",
    "In Review",
    "Interview Scheduled",
    "Technical Round",
    "HR Round",
    "Offer Received",
    "Accepted",
    "Rejected",
    "Withdrawn",
]

# (db column, what the user sees)
EDITABLE_FIELDS = [
    ("company", "Company"),
    ("internship_title", "Internship Title"),
    ("job_code", "Job Code"),
    ("date", "Date"),
    ("status", "Status"),
]

# has to be a raw string or the backslashes break everything. ask me how i know
LOGO = r"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   _____ _   _ _______ ______ _____  _   _  _____ _    _ _____║
║  |_   _| \ | |__   __|  ____|  __ \| \ | |/ ____| |  | |  __ ║
║    | | |  \| |  | |  | |__  | |__) |  \| | (___ | |__| | |__) ║
║    | | | . ` |  | |  |  __| |  _  /| . ` |\___ \|  __  |  ___/║
║   _| |_| |\  |  | |  | |____| | \ \| |\  |____) | |  | | |    ║
║  |_____|_| \_|  |_|  |______|_|  \_\_| \_|_____/|_|  |_|_|    ║
║                                                               ║
║               🎯 APPLICATION TRACKER 🎯                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""

class InternshipTracker:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.db_path = DB_PATH

    def connect_database(self):
        try:
            print("\n📊 Setting up database...")

            # makes the file if its not there
            self.connection = sqlite3.connect(self.db_path)
            # so i can do app["company"] instead of app[1] like a caveman
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()

            create_table_query = """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                internship_title TEXT NOT NULL,
                job_code TEXT,
                date TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            self.cursor.execute(create_table_query)
            self.connection.commit()

            print(f"✅ Database ready! (Stored in: {self.db_path})\n")
            return True

        except sqlite3.Error as e:
            print(f"❌ Error connecting to database: {e}")
            return False

    def clear_screen(self):
        os.system('clear' if os.name != 'nt' else 'cls')

    # ---- printing stuff ----

    def print_header(self, title):
        print("\n" + "="*60)
        print(f"           {title}")
        print("="*60 + "\n")

    def pause(self):
        input("\nPress Enter to continue...")

    def print_application(self, app):
        print(f"{'─'*60}")
        print(f"🆔 ID: {app['id']}")
        print(f"🏢 Company: {app['company']}")
        print(f"💼 Title: {app['internship_title']}")
        print(f"🔢 Job Code: {app['job_code'] or 'N/A'}")
        print(f"📅 Date: {app['date']}")
        print(f"📊 Status: {app['status']}")
        print(f"{'─'*60}")

    def print_applications(self, applications):
        for app in applications:
            self.print_application(app)
            print()

    def display_menu(self):
        print("\n" + "="*60)
        print("                    MAIN MENU")
        print("="*60)
        print("\n1. 📝 Insert New Application")
        print("2. 👀 View Saved Applications")
        print("3. 🔍 Search Applications")
        print("4. ✏️  Edit Application")
        print("5. 🗑️  Delete Application")
        print("6. 📈 View Stats")
        print("7. 💾 Download Applications (CSV)")
        print("8. 🌱 Start New Season")
        print("9. 🚪 Exit")
        print("\n" + "="*60)

    # ---- input stuff ----

    # keeps asking till u give a real YYYY-MM-DD date
    # blank = today, or None if default_today is off
    def prompt_date(self, prompt, default_today=True):
        while True:
            date_str = input(prompt).strip()
            if not date_str:
                return datetime.now().strftime('%Y-%m-%d') if default_today else None
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            except ValueError:
                print("❌ Invalid date format! Please use YYYY-MM-DD.")

    # blank returns the default, None = cancel
    def prompt_status(self, default=None):
        print("\nStatus Options:")
        for i, status in enumerate(STATUSES, 1):
            print(f"  {i}. {status}")

        hint = f"default: {default}" if default else "Enter to cancel"
        while True:
            choice = input(f"Status (1-{len(STATUSES)}, {hint}): ").strip()
            if not choice:
                return default
            if choice.isdigit() and 1 <= int(choice) <= len(STATUSES):
                return STATUSES[int(choice) - 1]
            # lets u type it out too, caps dont matter
            for status in STATUSES:
                if choice.lower() == status.lower():
                    return status
            print("❌ Invalid choice! Pick a number from the list.")

    # returns the row or None if it doesnt exist
    def find_application(self, action):
        app_id = input(f"Enter Application ID to {action}: ").strip()
        if not app_id.isdigit():
            print("❌ Invalid ID!")
            return None

        self.cursor.execute("SELECT * FROM applications WHERE id = ?", (int(app_id),))
        app = self.cursor.fetchone()
        if not app:
            print(f"❌ No application found with ID: {app_id}")
        return app

    # ---- the actual menu options ----

    def insert_application(self):
        self.print_header("📝 INSERT NEW APPLICATION")

        try:
            company = input("Company Name: ").strip()
            if not company:
                print("❌ Company name cannot be empty!")
                return

            # its always swe intern anyway lmao
            title = input("Internship Title (default: Software Engineer Intern): ").strip()
            if not title:
                title = "Software Engineer Intern"

            job_code = input("Job Code (optional): ").strip()

            date = self.prompt_date("Application Date (YYYY-MM-DD) or press Enter for today: ")

            status = self.prompt_status(default="Applied")

            query = """
            INSERT INTO applications (company, internship_title, job_code, date, status)
            VALUES (?, ?, ?, ?, ?)
            """
            values = (company, title, job_code, date, status)

            self.cursor.execute(query, values)
            self.connection.commit()

            print(f"\n✅ Application added successfully! (ID: {self.cursor.lastrowid})")

        except sqlite3.Error as e:
            print(f"❌ Error inserting application: {e}")

    def view_applications(self):
        self.print_header("👀 SAVED APPLICATIONS")

        try:
            self.cursor.execute("SELECT * FROM applications ORDER BY date DESC")
            applications = self.cursor.fetchall()

            if not applications:
                print("📭 No applications found. Start adding some!")
                return

            print(f"Total Applications: {len(applications)}\n")
            self.print_applications(applications)

        except sqlite3.Error as e:
            print(f"❌ Error retrieving applications: {e}")

    def search_applications(self):
        self.print_header("🔍 SEARCH APPLICATIONS")

        term = input("Search company, title, job code, or status: ").strip()
        if not term:
            print("❌ Search cancelled.")
            return

        try:
            # LIKE isnt case sensitive in sqlite which is nice, % = wildcard
            pattern = f"%{term}%"
            self.cursor.execute("""
                SELECT * FROM applications
                WHERE company LIKE ? OR internship_title LIKE ? OR job_code LIKE ? OR status LIKE ?
                ORDER BY date DESC
            """, (pattern, pattern, pattern, pattern))
            applications = self.cursor.fetchall()

            if not applications:
                print(f"📭 No applications match '{term}'.")
                return

            print(f"\nFound {len(applications)} matching application(s):\n")
            self.print_applications(applications)

        except sqlite3.Error as e:
            print(f"❌ Error searching applications: {e}")

    def edit_application(self):
        self.print_header("✏️  EDIT APPLICATION")

        try:
            app = self.find_application("edit")
            if not app:
                return

            print("\n📋 Current Application Details:")
            self.print_application(app)

            print("\nWhat would you like to edit?")
            for i, (_, label) in enumerate(EDITABLE_FIELDS, 1):
                print(f"{i}. {label}")
            cancel_choice = len(EDITABLE_FIELDS) + 1
            print(f"{cancel_choice}. Cancel")

            choice = input(f"\nEnter your choice (1-{cancel_choice}): ").strip()

            if choice == str(cancel_choice):
                print("❌ Edit cancelled.")
                return
            if not choice.isdigit() or not 1 <= int(choice) <= len(EDITABLE_FIELDS):
                print("❌ Invalid choice!")
                return

            column, label = EDITABLE_FIELDS[int(choice) - 1]

            if column == "date":
                new_value = self.prompt_date("Enter new Date (YYYY-MM-DD) or press Enter to cancel: ",
                                             default_today=False)
            elif column == "status":
                new_value = self.prompt_status()
            else:
                new_value = input(f"Enter new {label}: ").strip()

            # job code can be blank, everything else cant
            if not new_value and column != "job_code":
                print("❌ Edit cancelled.")
                return

            # f string in sql is fine here i promise, column only comes from EDITABLE_FIELDS not the user
            # (no bobby tables today)
            self.cursor.execute(f"UPDATE applications SET {column} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                                (new_value, app["id"]))
            self.connection.commit()
            print(f"✅ {label} updated successfully!")

        except sqlite3.Error as e:
            print(f"❌ Error editing application: {e}")

    def delete_application(self):
        self.print_header("🗑️  DELETE APPLICATION")

        try:
            app = self.find_application("delete")
            if not app:
                return

            print("\n📋 Application to Delete:")
            self.print_application(app)

            confirm = input("\n⚠️  Are you sure you want to delete this? (yes/no): ").strip().lower()

            if confirm == 'yes':
                self.cursor.execute("DELETE FROM applications WHERE id = ?", (app["id"],))
                self.connection.commit()
                print("✅ Application deleted successfully!")
            else:
                print("❌ Deletion cancelled.")

        except sqlite3.Error as e:
            print(f"❌ Error deleting application: {e}")

    # how many in each status aka how many rejections ive collected 💀
    def show_stats(self):
        self.print_header("📈 APPLICATION STATS")

        try:
            self.cursor.execute("""
                SELECT status, COUNT(*) AS count FROM applications
                GROUP BY status ORDER BY count DESC
            """)
            rows = self.cursor.fetchall()

            if not rows:
                print("📭 No applications yet. Start adding some!")
                return

            total = sum(row["count"] for row in rows)
            print(f"Total Applications: {total}\n")
            for row in rows:
                print(f"  {row['status']:<22} {row['count']:>4}")

        except sqlite3.Error as e:
            print(f"❌ Error loading stats: {e}")

    # dumps everything to a csv in exports/ with a timestamp
    # gives back (path, count) or (None, 0) if theres nothing
    def export_csv(self, prefix="internship_applications"):
        self.cursor.execute("""
            SELECT id, company, internship_title, job_code, date, status
            FROM applications ORDER BY date
        """)
        applications = self.cursor.fetchall()
        if not applications:
            return None, 0

        EXPORT_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = EXPORT_DIR / f"{prefix}_{timestamp}.csv"

        with open(path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Company', 'Internship Title', 'Job Code', 'Date', 'Status'])
            writer.writerows(applications)

        return path, len(applications)

    def download_csv(self):
        self.print_header("💾 DOWNLOAD APPLICATIONS (CSV)")

        try:
            path, count = self.export_csv()
            if not path:
                print("📭 No applications to download!")
                return

            print(f"✅ Successfully exported {count} applications!")
            print(f"📁 File saved as: {path.name}")
            print(f"📍 Location: {path}")

        except sqlite3.Error as e:
            print(f"❌ Error downloading applications: {e}")
        except OSError as e:
            print(f"❌ Error writing CSV file: {e}")

    # new recruiting season new me. backs up + archives the old db and starts fresh
    def start_new_season(self):
        self.print_header("🌱 START NEW SEASON")

        print("This will:")
        print("  1. Export all current applications to a CSV in exports/")
        print("  2. Move the current database into archive/")
        print("  3. Start a fresh, empty database (IDs restart at 1)\n")

        confirm = input("⚠️  Start a new season? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ New season cancelled.")
            return

        started = False
        try:
            path, count = self.export_csv(prefix="season_backup")
            if path:
                print(f"💾 Exported {count} applications to: {path}")

            # gotta close it first or windows wont let u move the file
            self.close()
            ARCHIVE_DIR.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archived = ARCHIVE_DIR / f"internship_tracker_{timestamp}.db"
            self.db_path.rename(archived)
            print(f"📦 Old database archived to: {archived}")
            started = True

        except (sqlite3.Error, OSError) as e:
            print(f"❌ Error starting new season: {e}")
            print("Your existing data was left in place.")

        # reconnect either way. if it worked u get a fresh db, if not it just reopens the old one
        self.close()
        if not self.connect_database():
            print("\n❌ Failed to connect to database. Exiting...")
            sys.exit(1)

        if started:
            print("🎉 New season started! Good luck! 🍀")

    def run(self):
        self.clear_screen()
        print(LOGO)
        print("\n🎓 Welcome to the Internship Application Tracker!")
        print("Track all your internship applications in one place.\n")

        if not self.connect_database():
            print("\n❌ Failed to connect to database. Exiting...")
            sys.exit(1)

        actions = {
            '1': self.insert_application,
            '2': self.view_applications,
            '3': self.search_applications,
            '4': self.edit_application,
            '5': self.delete_application,
            '6': self.show_stats,
            '7': self.download_csv,
            '8': self.start_new_season,
        }

        while True:
            self.display_menu()
            choice = input("\nEnter your choice (1-9): ").strip()

            if choice == '9':
                print("\n👋 Thank you for using Internship Application Tracker!")
                print("Good luck with your applications! 🍀\n")
                break

            action = actions.get(choice)
            if action:
                action()
            else:
                print("\n❌ Invalid choice! Please enter a number between 1-9.")
            self.pause()

    def close(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None

def main():
    tracker = InternshipTracker()
    try:
        tracker.run()
    except (KeyboardInterrupt, EOFError):
        print("\n\n👋 Application interrupted. Goodbye!")
    finally:
        tracker.close()

if __name__ == "__main__":
    main()
