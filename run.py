"""
Code Everyday • Multi-Environment Launcher Script
Supports development mode (Flask built-in server) and production WSGI (Waitress on Windows, Gunicorn on Linux).

Run with:
    python run.py
"""

import os
import sys

from app import app, init_db

if __name__ == '__main__':
    # Ensure database schema, tables, and multi-language stubs are initialized
    init_db()

    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() in ('true', '1', 'yes')

    print("\n" + "=" * 65)
    print("🔥 Starting Code Everyday • Daily Coding & Streak Platform")
    print(f"📍 Local URL: http://{host}:{port}")
    print("🔐 Database: SQLite (auth.db)")
    print("💻 Languages: Python 3, Java (OpenJDK), C (GCC), C++ (G++)")
    print("👤 Pre-seeded User: alex.taylor@example.com (Pass: ApexGuard#2026!)")
    print("=" * 65 + "\n")

    if debug:
        app.run(host=host, port=port, debug=True)
    else:
        try:
            from waitress import serve
            print("🚀 Serving in Production Mode using Waitress WSGI...")
            serve(app, host=host, port=port)
        except ImportError:
            print("⚠️ Waitress not found, running via standard server...")
            app.run(host=host, port=port, debug=False)
