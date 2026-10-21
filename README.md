# 🎯 Internship Application Tracker

A terminal-based Python application to manage and track your internship applications. Data is stored in a local SQLite database, so there is no server to install or configure.

## ✨ Features

- **📝 Insert New Applications**: Add internship applications with company name, title, job code, date, and status
- **👀 View Applications**: See all your saved applications, newest first
- **🔍 Search**: Find applications by company, title, job code, or status
- **✏️ Edit Applications**: Update any field of existing applications
- **🗑️ Delete Applications**: Remove applications you no longer need to track
- **📈 Stats**: See how many applications are in each status
- **💾 CSV Export**: Download all your applications as a CSV file
- **🌱 New Season**: Back up and archive this season's applications and start fresh
- **🎨 Beautiful ASCII UI**: Clean terminal interface with emojis and ASCII art

## 📋 Requirements

- Python 3.6 or higher
- No extra packages (only the standard library is used)

## 🎮 Usage

```bash
python main.py
```

On macOS/Linux you may need `python3 main.py`.

On first run the app creates `internship_tracker.db` next to `main.py`. It always uses that file, no matter which folder you run the command from.

## 📊 Database Schema

```sql
applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    internship_title TEXT NOT NULL,
    job_code TEXT,
    date TEXT NOT NULL,          -- YYYY-MM-DD
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## 🎯 Application Fields

- **ID**: Auto-generated unique identifier
- **Company**: Name of the company (required)
- **Internship Title**: Position/role title (defaults to "Software Engineer Intern")
- **Job Code**: Job posting reference number (optional)
- **Date**: Application submission date (YYYY-MM-DD, defaults to today)
- **Status**: Current application status (defaults to "Applied")

## 📝 Status Options

Statuses are picked from a numbered list so they stay consistent:

1. Applied
2. In Review
3. Interview Scheduled
4. Technical Round
5. HR Round
6. Offer Received
7. Accepted
8. Rejected
9. Withdrawn

## 🌱 Starting a New Season

Choose **8. Start New Season** from the main menu. After you confirm, the app will:

1. Export every current application to `exports/season_backup_<timestamp>.csv`
2. Move the database to `archive/internship_tracker_<timestamp>.db`
3. Create a fresh, empty database (IDs restart at 1)

Nothing is deleted. To look at an old season again, copy its file from `archive/` back to `internship_tracker.db`.

## 📁 File Structure

```
.
├── main.py                  # Main application file
├── requirements.txt         # No dependencies (standard library only)
├── README.md                # This file
├── internship_tracker.db    # Your data (created on first run)
├── exports/                 # CSV exports
└── archive/                 # Databases from past seasons
```

## 💡 Tips

1. **CSV Export**: Files are saved with timestamps to avoid overwriting
2. **Regular Updates**: Keep your application statuses updated for better tracking
3. **Backup**: Periodically export to CSV for backup purposes

## 📄 License

Free to use for personal and educational purposes.

## 🎓 Good Luck!

May all your internship applications result in offers! 🍀✨
