"""
Code Everyday • Daily Programming Platform & Multilingual Execution Engine
C, C++, Java, and Python Challenge Runner with Secret Hidden Test Cases,
SQLite Problem Bank, Google Gemini 2.5 Flash Generation, and Streak Engine.
"""

import os
import re
import json
import random
import sqlite3
import shutil
import tempfile
import subprocess
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'code-everyday-secure-session-key-2026')
app.permanent_session_lifetime = timedelta(days=30)

DATABASE = os.path.join(os.path.dirname(__file__), 'auth.db')
DEFAULT_GEMINI_API_KEY = ""

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ==============================================================================
# Database Schema & Initialization
# ==============================================================================

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()

        # Users table with streak tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                current_streak INTEGER DEFAULT 0,
                max_streak INTEGER DEFAULT 0,
                last_streak_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Password Resets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                token TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # App Settings (stores Gemini API key)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')

        # Save default Gemini key if not present
        cursor.execute("SELECT value FROM app_settings WHERE key = 'gemini_api_key'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO app_settings (key, value) VALUES ('gemini_api_key', ?)", (DEFAULT_GEMINI_API_KEY,))

        # Check problems table schema compatibility
        cursor.execute("PRAGMA table_info(problems)")
        existing_cols = {c[1] for c in cursor.fetchall()}
        if existing_cols and 'hidden_test_cases' not in existing_cols:
            cursor.execute("DROP TABLE IF EXISTS user_submissions")
            cursor.execute("DROP TABLE IF EXISTS problems")

        # Problems bank table with separate public and hidden test cases
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                difficulty TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                starter_code TEXT NOT NULL,
                sample_input TEXT NOT NULL,
                sample_output TEXT NOT NULL,
                public_test_cases TEXT NOT NULL,
                hidden_test_cases TEXT NOT NULL,
                assigned_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # User Submissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                problem_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                code TEXT,
                language TEXT DEFAULT 'python',
                is_daily BOOLEAN DEFAULT 0,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (problem_id) REFERENCES problems (id)
            )
        ''')

        # Check user_submissions table migration for language column
        cursor.execute("PRAGMA table_info(user_submissions)")
        sub_cols = {c[1] for c in cursor.fetchall()}
        if sub_cols and 'language' not in sub_cols:
            cursor.execute("ALTER TABLE user_submissions ADD COLUMN language TEXT DEFAULT 'python'")

        # Pre-seed demo user if not present
        cursor.execute('SELECT id FROM users WHERE email = ?', ('alex.taylor@example.com',))
        if not cursor.fetchone():
            demo_hash = generate_password_hash('ApexGuard#2026!')
            cursor.execute('''
                INSERT INTO users (name, email, password_hash, current_streak, max_streak)
                VALUES (?, ?, ?, 3, 5)
            ''', ('Alex Taylor', 'alex.taylor@example.com', demo_hash))

        # Pre-seed initial problem bank with public and hidden test cases
        seed_problem_bank(cursor)
        conn.commit()


def seed_problem_bank(cursor):
    """Pre-seeds standard algorithmic problems with public and hidden edge cases."""
    initial_problems = [
        {
            'title': 'Two Sum',
            'slug': 'two-sum',
            'difficulty': 'Easy',
            'category': 'Arrays & Hash Maps',
            'description': 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.\n\nConstraints:\n- 2 <= len(nums) <= 10^4\n- -10^9 <= nums[i] <= 10^9',
            'starter_code': 'def two_sum(nums, target):\n    # Write your solution here\n    pass',
            'sample_input': 'nums = [2, 7, 11, 15], target = 9',
            'sample_output': '[0, 1]',
            'public_test_cases': json.dumps([
                {'input': {'nums': [2, 7, 11, 15], 'target': 9}, 'expected': [0, 1]},
                {'input': {'nums': [3, 2, 4], 'target': 6}, 'expected': [1, 2]}
            ]),
            'hidden_test_cases': json.dumps([
                {'input': {'nums': [3, 3], 'target': 6}, 'expected': [0, 1]},
                {'input': {'nums': [-1, -2, -3, -4, -5], 'target': -8}, 'expected': [2, 4]},
                {'input': {'nums': [0, 4, 3, 0], 'target': 0}, 'expected': [0, 3]}
            ])
        },
        {
            'title': 'Valid Palindrome',
            'slug': 'valid-palindrome',
            'difficulty': 'Easy',
            'category': 'Strings',
            'description': 'A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward.\n\nReturn True if the given string s is a palindrome, or False otherwise.',
            'starter_code': 'def is_palindrome(s):\n    # Write your solution here\n    pass',
            'sample_input': 's = "A man, a plan, a canal: Panama"',
            'sample_output': 'True',
            'public_test_cases': json.dumps([
                {'input': {'s': 'A man, a plan, a canal: Panama'}, 'expected': True},
                {'input': {'s': 'race a car'}, 'expected': False}
            ]),
            'hidden_test_cases': json.dumps([
                {'input': {'s': ' '}, 'expected': True},
                {'input': {'s': '0P'}, 'expected': False},
                {'input': {'s': 'a.'}, 'expected': True},
                {'input': {'s': 'No lemon, no melon'}, 'expected': True}
            ])
        },
        {
            'title': 'Reverse Integer',
            'slug': 'reverse-integer',
            'difficulty': 'Medium',
            'category': 'Math',
            'description': 'Given a signed 32-bit integer x, return x with its digits reversed. If reversing x causes the value to go outside the signed 32-bit integer range [-2^31, 2^31 - 1], then return 0.',
            'starter_code': 'def reverse_integer(x):\n    # Write your solution here\n    pass',
            'sample_input': 'x = 123',
            'sample_output': '321',
            'public_test_cases': json.dumps([
                {'input': {'x': 123}, 'expected': 321},
                {'input': {'x': -123}, 'expected': -321}
            ]),
            'hidden_test_cases': json.dumps([
                {'input': {'x': 120}, 'expected': 21},
                {'input': {'x': 0}, 'expected': 0},
                {'input': {'x': 1534236469}, 'expected': 0}
            ])
        },
        {
            'title': 'Maximum Subarray (Kadane)',
            'slug': 'maximum-subarray',
            'difficulty': 'Medium',
            'category': 'Dynamic Programming',
            'description': 'Given an integer array nums, find the subarray with the largest sum, and return its sum.',
            'starter_code': 'def max_sub_array(nums):\n    # Write your solution here\n    pass',
            'sample_input': 'nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]',
            'sample_output': '6',
            'public_test_cases': json.dumps([
                {'input': {'nums': [-2, 1, -3, 4, -1, 2, 1, -5, 4]}, 'expected': 6},
                {'input': {'nums': [1]}, 'expected': 1}
            ]),
            'hidden_test_cases': json.dumps([
                {'input': {'nums': [5, 4, -1, 7, 8]}, 'expected': 23},
                {'input': {'nums': [-1]}, 'expected': -1},
                {'input': {'nums': [-2, -1]}, 'expected': -1}
            ])
        },
        {
            'title': 'Valid Parentheses',
            'slug': 'valid-parentheses',
            'difficulty': 'Easy',
            'category': 'Stacks',
            'description': 'Given a string s containing just the characters "(", ")", "{", "}", "[" and "]", determine if the input string is valid.\n\nOpen brackets must be closed by the same type of brackets, and closed in the correct order.',
            'starter_code': 'def is_valid_parentheses(s):\n    # Write your solution here\n    pass',
            'sample_input': 's = "()[]{}"',
            'sample_output': 'True',
            'public_test_cases': json.dumps([
                {'input': {'s': '()'}, 'expected': True},
                {'input': {'s': '()[]{}'}, 'expected': True}
            ]),
            'hidden_test_cases': json.dumps([
                {'input': {'s': '(]'}, 'expected': False},
                {'input': {'s': '([)]'}, 'expected': False},
                {'input': {'s': '{[]}'}, 'expected': True},
                {'input': {'s': '['}, 'expected': False}
            ])
        },
        {
            'title': 'Climbing Stairs',
            'slug': 'climbing-stairs',
            'difficulty': 'Easy',
            'category': 'Dynamic Programming',
            'description': 'You are climbing a staircase. It takes n steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?',
            'starter_code': 'def climb_stairs(n):\n    # Write your solution here\n    pass',
            'sample_input': 'n = 3',
            'sample_output': '3',
            'public_test_cases': json.dumps([
                {'input': {'n': 2}, 'expected': 2},
                {'input': {'n': 3}, 'expected': 3}
            ]),
            'hidden_test_cases': json.dumps([
                {'input': {'n': 1}, 'expected': 1},
                {'input': {'n': 4}, 'expected': 5},
                {'input': {'n': 5}, 'expected': 8}
            ])
        },
        {
            'title': 'Single Number',
            'slug': 'single-number',
            'difficulty': 'Easy',
            'category': 'Bit Manipulation',
            'description': 'Given a non-empty array of integers nums, every element appears twice except for one. Find that single one.\n\nYou must implement a solution with a linear runtime complexity and use only constant extra space.',
            'starter_code': 'def single_number(nums):\n    # Write your solution here\n    pass',
            'sample_input': 'nums = [4, 1, 2, 1, 2]',
            'sample_output': '4',
            'public_test_cases': json.dumps([
                {'input': {'nums': [2, 2, 1]}, 'expected': 1},
                {'input': {'nums': [4, 1, 2, 1, 2]}, 'expected': 4}
            ]),
            'hidden_test_cases': json.dumps([
                {'input': {'nums': [1]}, 'expected': 1},
                {'input': {'nums': [-1, -1, -2]}, 'expected': -2},
                {'input': {'nums': [10, 20, 30, 20, 10]}, 'expected': 30}
            ])
        }
    ]

    for prob in initial_problems:
        cursor.execute('SELECT id FROM problems WHERE slug = ?', (prob['slug'],))
        existing = cursor.fetchone()
        if not existing:
            cursor.execute('''
                INSERT INTO problems (title, slug, difficulty, category, description, starter_code, sample_input, sample_output, public_test_cases, hidden_test_cases)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prob['title'],
                prob['slug'],
                prob['difficulty'],
                prob['category'],
                prob['description'],
                prob['starter_code'],
                prob['sample_input'],
                prob['sample_output'],
                prob['public_test_cases'],
                prob['hidden_test_cases']
            ))
        else:
            # Update existing problem to clear out any old pre-filled solutions!
            cursor.execute('''
                UPDATE problems
                SET starter_code = ?, public_test_cases = ?, hidden_test_cases = ?
                WHERE slug = ?
            ''', (prob['starter_code'], prob['public_test_cases'], prob['hidden_test_cases'], prob['slug']))


# Multi-Language Starter Code Stubs (Empty scaffolds with no solutions)
PROBLEM_STARTER_CODES = {
    'two-sum': {
        'python': 'def two_sum(nums, target):\n    # Write your solution here\n    pass',
        'c': '#include <stdlib.h>\n\n/**\n * Note: The returned array must be malloced.\n */\nint* twoSum(int* nums, int numsSize, int target, int* returnSize) {\n    // Write your solution here\n    *returnSize = 2;\n    return NULL;\n}',
        'cpp': '#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        // Write your solution here\n        return {};\n    }\n};',
        'java': 'class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        // Write your solution here\n        return new int[0];\n    }\n}'
    },
    'valid-palindrome': {
        'python': 'def is_palindrome(s):\n    # Write your solution here\n    pass',
        'c': '#include <stdbool.h>\n#include <string.h>\n\nbool isPalindrome(char* s) {\n    // Write your solution here\n    return false;\n}',
        'cpp': '#include <string>\nusing namespace std;\n\nclass Solution {\npublic:\n    bool isPalindrome(string s) {\n        // Write your solution here\n        return false;\n    }\n};',
        'java': 'class Solution {\n    public boolean isPalindrome(String s) {\n        // Write your solution here\n        return false;\n    }\n}'
    },
    'reverse-integer': {
        'python': 'def reverse_integer(x):\n    # Write your solution here\n    pass',
        'c': 'int reverseInteger(int x) {\n    // Write your solution here\n    return 0;\n}',
        'cpp': 'class Solution {\npublic:\n    int reverseInteger(int x) {\n        // Write your solution here\n        return 0;\n    }\n};',
        'java': 'class Solution {\n    public int reverseInteger(int x) {\n        // Write your solution here\n        return 0;\n    }\n}'
    },
    'maximum-subarray': {
        'python': 'def max_sub_array(nums):\n    # Write your solution here\n    pass',
        'c': 'int maxSubArray(int* nums, int numsSize) {\n    // Write your solution here\n    return 0;\n}',
        'cpp': '#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    int maxSubArray(vector<int>& nums) {\n        // Write your solution here\n        return 0;\n    }\n};',
        'java': 'class Solution {\n    public int maxSubArray(int[] nums) {\n        // Write your solution here\n        return 0;\n    }\n}'
    },
    'valid-parentheses': {
        'python': 'def is_valid_parentheses(s):\n    # Write your solution here\n    pass',
        'c': '#include <stdbool.h>\n\nbool isValidParentheses(char* s) {\n    // Write your solution here\n    return false;\n}',
        'cpp': '#include <string>\nusing namespace std;\n\nclass Solution {\npublic:\n    bool isValidParentheses(string s) {\n        // Write your solution here\n        return false;\n    }\n};',
        'java': 'class Solution {\n    public boolean isValidParentheses(String s) {\n        // Write your solution here\n        return false;\n    }\n}'
    },
    'climbing-stairs': {
        'python': 'def climb_stairs(n):\n    # Write your solution here\n    pass',
        'c': 'int climbStairs(int n) {\n    // Write your solution here\n    return 0;\n}',
        'cpp': 'class Solution {\npublic:\n    int climbStairs(int n) {\n        // Write your solution here\n        return 0;\n    }\n};',
        'java': 'class Solution {\n    public int climbStairs(int n) {\n        // Write your solution here\n        return 0;\n    }\n}'
    },
    'single-number': {
        'python': 'def single_number(nums):\n    # Write your solution here\n    pass',
        'c': 'int singleNumber(int* nums, int numsSize) {\n    // Write your solution here\n    return 0;\n}',
        'cpp': '#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    int singleNumber(vector<int>& nums) {\n        // Write your solution here\n        return 0;\n    }\n};',
        'java': 'class Solution {\n    public int singleNumber(int[] nums) {\n        // Write your solution here\n        return 0;\n    }\n}'
    }
}


def get_problem_starter_codes(problem_row):
    """Returns a dict of starter codes for Python, C, C++, and Java (no solutions)."""
    if not problem_row:
        return {
            'python': 'def solution():\n    # Write your solution here\n    pass',
            'c': '// Write your solution in C here\n',
            'cpp': '// Write your solution in C++ here\n',
            'java': '// Write your solution in Java here\nclass Solution {\n}\n'
        }
    slug = problem_row.get('slug', '')
    for k, v in PROBLEM_STARTER_CODES.items():
        if k in slug:
            return v

    py_code = problem_row.get('starter_code', 'def solution():\n    # Write your solution here\n    pass')
    # If the starter code in DB still has a solution, strip everything after signature
    if 'def ' in py_code:
        lines = py_code.splitlines()
        sig = lines[0] if lines else 'def solution():'
        py_clean = f"{sig}\n    # Write your solution here\n    pass"
    else:
        py_clean = py_code

    return {
        'python': py_clean,
        'c': '// Write your solution in C here\n',
        'cpp': '// Write your solution in C++ here\n#include <iostream>\nusing namespace std;\n\nclass Solution {\npublic:\n    // Write your method here\n};\n',
        'java': '// Write your solution in Java here\nclass Solution {\n    // Write your method here\n}\n'
    }


init_db()

EMAIL_REGEX = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')

def validate_password_complexity(pwd: str):
    if len(pwd) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', pwd):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[0-9]', pwd):
        return False, "Password must contain at least one number."
    if not re.search(r'[^A-Za-z0-9]', pwd):
        return False, "Password must contain at least one special symbol."
    return True, ""


# ==============================================================================
# Gemini 2.5 Flash API Daily Question Generation
# ==============================================================================

def get_gemini_api_key():
    """Retrieve Gemini API key from database settings or environment or default."""
    with get_db() as conn:
        row = conn.execute("SELECT value FROM app_settings WHERE key = 'gemini_api_key'").fetchone()
        if row and row['value']:
            return row['value'].strip()
    return os.environ.get('GEMINI_API_KEY', DEFAULT_GEMINI_API_KEY).strip()


def generate_question_with_gemini(api_key: str):
    """
    Calls Google Gemini 2.5 Flash API to generate an algorithmic challenge
    with separate public test cases and hidden edge test cases using structured schema.
    """
    if not api_key:
        return None

    prompt = (
        "You are an expert algorithms challenge creator for Code Everyday. "
        "Create an algorithmic programming challenge for Python 3. "
        "Provide 2 public test cases and 3-4 hidden edge test cases (e.g. boundary conditions, empty/single element, negative numbers, extreme values). "
        "The starter_code must be an empty template signature containing only '# Write your solution here\\n    pass'. "
        "DO NOT provide any working solution or answer under any circumstances. Users must write the code themselves."
    )

    schema = {
        "type": "OBJECT",
        "properties": {
            "title": {"type": "STRING"},
            "difficulty": {"type": "STRING"},
            "category": {"type": "STRING"},
            "description": {"type": "STRING"},
            "starter_code": {"type": "STRING"},
            "sample_input": {"type": "STRING"},
            "sample_output": {"type": "STRING"},
            "public_test_cases": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "input": {"type": "OBJECT"},
                        "expected": {}
                    },
                    "required": ["input", "expected"]
                }
            },
            "hidden_test_cases": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "input": {"type": "OBJECT"},
                        "expected": {}
                    },
                    "required": ["input", "expected"]
                }
            }
        },
        "required": [
            "title", "difficulty", "category", "description",
            "starter_code", "sample_input", "sample_output",
            "public_test_cases", "hidden_test_cases"
        ]
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "response_mime_type": "application/json",
            "response_schema": schema,
            "maxOutputTokens": 4096
        }
    }).encode('utf-8')

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            result = json.loads(response.read().decode('utf-8'))
            candidates = result.get('candidates', [])
            if candidates:
                raw_text = candidates[0]['content']['parts'][0]['text'].strip()
                if raw_text.startswith("```"):
                    raw_text = re.sub(r"^```[a-zA-Z]*\n?", "", raw_text)
                    raw_text = re.sub(r"\n?```$", "", raw_text)
                problem_data = json.loads(raw_text.strip(), strict=False)
                return problem_data
    except Exception as e:
        print(f"[Gemini 2.5 Flash] Generation error: {e}")
        return None


def get_or_create_daily_problem():
    """
    Returns today's question.
    GUARANTEE: All users receive the exact same question each day because it is
    saved in SQLite with assigned_date = YYYY-MM-DD.
    """
    today_str = datetime.now().strftime('%Y-%m-%d')

    def attach_hidden_count(p_dict):
        if not p_dict:
            return None
        try:
            p_dict['hidden_test_cases_count'] = len(json.loads(p_dict.get('hidden_test_cases', '[]')))
        except Exception:
            p_dict['hidden_test_cases_count'] = 0
        p_dict['starter_codes'] = get_problem_starter_codes(p_dict)
        return p_dict

    with get_db() as conn:
        # Check if today's problem is already generated & saved in SQLite
        problem = conn.execute('SELECT * FROM problems WHERE assigned_date = ?', (today_str,)).fetchone()
        if problem:
            return attach_hidden_count(dict(problem))

        # Generate fresh question using Gemini with hidden test cases
        api_key = get_gemini_api_key()
        gemini_prob = generate_question_with_gemini(api_key)

        if gemini_prob and gemini_prob.get('title'):
            title = gemini_prob.get('title', 'Daily Challenge').strip()
            slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-') + f"-{today_str}"
            public_cases = json.dumps(gemini_prob.get('public_test_cases', []))
            hidden_cases = json.dumps(gemini_prob.get('hidden_test_cases', []))

            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO problems (title, slug, difficulty, category, description, starter_code, sample_input, sample_output, public_test_cases, hidden_test_cases, assigned_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                title,
                slug,
                gemini_prob.get('difficulty', 'Medium'),
                gemini_prob.get('category', 'Algorithms'),
                gemini_prob.get('description', ''),
                gemini_prob.get('starter_code', 'def solution():\n    pass'),
                gemini_prob.get('sample_input', ''),
                gemini_prob.get('sample_output', ''),
                public_cases,
                hidden_cases,
                today_str
            ))
            conn.commit()
            new_id = cursor.lastrowid
            return attach_hidden_count(dict(conn.execute('SELECT * FROM problems WHERE id = ?', (new_id,)).fetchone()))

        # Fallback: pick deterministically from seeded problems
        all_problems = conn.execute('SELECT id FROM problems ORDER BY id ASC').fetchall()
        if all_problems:
            day_seed = int(today_str.replace('-', ''))
            chosen_id = all_problems[day_seed % len(all_problems)]['id']
            conn.execute('UPDATE problems SET assigned_date = ? WHERE id = ?', (today_str, chosen_id))
            conn.commit()
            return attach_hidden_count(dict(conn.execute('SELECT * FROM problems WHERE id = ?', (chosen_id,)).fetchone()))

        return None


# ==============================================================================
# Streak Calculation Engine
# ==============================================================================

def update_user_streak(user_id: int):
    """Updates user's streak when today's daily question is solved."""
    today_str = datetime.now().strftime('%Y-%m-%d')
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    with get_db() as conn:
        user = conn.execute('SELECT current_streak, max_streak, last_streak_date FROM users WHERE id = ?', (user_id,)).fetchone()
        if not user:
            return 0, 0, False

        curr_streak = user['current_streak'] or 0
        max_streak = user['max_streak'] or 0
        last_date = user['last_streak_date']

        # Already claimed today
        if last_date == today_str:
            return curr_streak, max_streak, False

        # Consecutive day (solved yesterday)
        if last_date == yesterday_str:
            new_streak = curr_streak + 1
        else:
            new_streak = 1

        new_max = max(max_streak, new_streak)

        conn.execute('''
            UPDATE users
            SET current_streak = ?, max_streak = ?, last_streak_date = ?
            WHERE id = ?
        ''', (new_streak, new_max, today_str, user_id))
        conn.commit()

        return new_streak, new_max, True


# ==============================================================================
# HTML Page Routes
# ==============================================================================

@app.route('/')
def index():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('index'))

    with get_db() as conn:
        user = conn.execute('SELECT id, name, email, current_streak, max_streak, created_at FROM users WHERE id = ?', (user_id,)).fetchone()

    if not user:
        session.clear()
        return redirect(url_for('index'))

    daily_prob = get_or_create_daily_problem()
    has_gemini = bool(get_gemini_api_key())
    return render_template('dashboard.html', user=dict(user), daily_problem=daily_prob, has_gemini_key=has_gemini)


# ==============================================================================
# REST API Endpoints: Auth
# ==============================================================================

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''
    confirm_password = data.get('confirmPassword') or ''

    if not name or len(name) < 2:
        return jsonify({'error': 'Full name must be at least 2 characters.'}), 400

    if not email or not EMAIL_REGEX.match(email):
        return jsonify({'error': 'Please provide a valid email address.'}), 400

    is_valid, msg = validate_password_complexity(password)
    if not is_valid:
        return jsonify({'error': msg}), 400

    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match.'}), 400

    password_hash = generate_password_hash(password)

    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (name, email, password_hash, current_streak, max_streak)
                VALUES (?, ?, ?, 0, 0)
            ''', (name, email, password_hash))
            conn.commit()
            new_user_id = cursor.lastrowid

        session.clear()
        session['user_id'] = new_user_id
        session.permanent = True

        return jsonify({
            'success': True,
            'message': f'Welcome aboard, {name}! Your account has been created.',
            'redirect': url_for('dashboard'),
            'user': {'id': new_user_id, 'name': name, 'email': email, 'current_streak': 0}
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({'error': 'An account with this email address already exists.'}), 409
    except Exception:
        return jsonify({'error': 'Registration failed. Please try again.'}), 500


@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''
    remember = bool(data.get('remember', False))

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    with get_db() as conn:
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Invalid email or password. Please check your credentials.'}), 401

    session.clear()
    session['user_id'] = user['id']
    if remember:
        session.permanent = True

    return jsonify({
        'success': True,
        'message': f'Welcome back, {user["name"]}!',
        'redirect': url_for('dashboard'),
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'current_streak': user['current_streak']
        }
    }), 200


@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Signed out successfully.',
        'redirect': url_for('index')
    }), 200


@app.route('/api/auth/forgot-password', methods=['POST'])
def api_forgot_password():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip()

    if not email or not EMAIL_REGEX.match(email):
        return jsonify({'error': 'Please provide a valid registered email address.'}), 400

    token = f"{random.randint(100000, 999999)}"

    with get_db() as conn:
        conn.execute('INSERT INTO password_resets (email, token) VALUES (?, ?)', (email, token))
        conn.commit()

    return jsonify({
        'success': True,
        'message': f'Recovery code {token} dispatched to {email}.',
        'token_preview': token
    }), 200


# ==============================================================================
# REST API Endpoints: Daily Question, Problems Bank, Hidden Test Cases
# ==============================================================================

@app.route('/api/daily-problem', methods=['GET'])
def api_daily_problem():
    user_id = session.get('user_id')
    problem = get_or_create_daily_problem()
    if not problem:
        return jsonify({'error': 'Unable to load daily problem.'}), 500

    is_solved = False
    current_streak = 0
    if user_id:
        with get_db() as conn:
            sub = conn.execute('''
                SELECT id FROM user_submissions
                WHERE user_id = ? AND problem_id = ? AND status = 'Accepted'
            ''', (user_id, problem['id'])).fetchone()
            is_solved = bool(sub)

            user = conn.execute('SELECT current_streak FROM users WHERE id = ?', (user_id,)).fetchone()
            if user:
                current_streak = user['current_streak']

    # Parse public test cases ONLY (keep hidden test cases secret on the server!)
    try:
        public_test_cases = json.loads(problem['public_test_cases'])
    except Exception:
        public_test_cases = []

    try:
        hidden_count = len(json.loads(problem['hidden_test_cases']))
    except Exception:
        hidden_count = 0

    starter_codes = get_problem_starter_codes(dict(problem))

    return jsonify({
        'problem': {
            'id': problem['id'],
            'title': problem['title'],
            'difficulty': problem['difficulty'],
            'category': problem['category'],
            'description': problem['description'],
            'starter_code': starter_codes.get('python', problem['starter_code']),
            'starter_codes': starter_codes,
            'sample_input': problem['sample_input'],
            'sample_output': problem['sample_output'],
            'public_test_cases': public_test_cases,
            'hidden_test_cases_count': hidden_count
        },
        'is_solved_by_user': is_solved,
        'current_streak': current_streak,
        'assigned_date': problem.get('assigned_date') or datetime.now().strftime('%Y-%m-%d')
    }), 200


@app.route('/api/problems', methods=['GET'])
def api_problems():
    user_id = session.get('user_id')

    with get_db() as conn:
        problems = conn.execute('SELECT id, title, slug, difficulty, category, description, assigned_date FROM problems ORDER BY id ASC').fetchall()

        solved_ids = set()
        if user_id:
            solved_rows = conn.execute('''
                SELECT DISTINCT problem_id FROM user_submissions
                WHERE user_id = ? AND status = 'Accepted'
            ''', (user_id,)).fetchall()
            solved_ids = {r['problem_id'] for r in solved_rows}

    problem_list = []
    for p in problems:
        problem_list.append({
            'id': p['id'],
            'title': p['title'],
            'slug': p['slug'],
            'difficulty': p['difficulty'],
            'category': p['category'],
            'description': p['description'],
            'is_daily': bool(p['assigned_date'] == datetime.now().strftime('%Y-%m-%d')),
            'is_solved': p['id'] in solved_ids
        })

    return jsonify({'problems': problem_list}), 200


@app.route('/api/problems/<int:problem_id>', methods=['GET'])
def api_problem_detail(problem_id):
    user_id = session.get('user_id')

    with get_db() as conn:
        p = conn.execute('SELECT * FROM problems WHERE id = ?', (problem_id,)).fetchone()
        if not p:
            return jsonify({'error': 'Problem not found.'}), 404

        is_solved = False
        if user_id:
            sub = conn.execute('SELECT id FROM user_submissions WHERE user_id = ? AND problem_id = ? AND status = "Accepted"', (user_id, problem_id)).fetchone()
            is_solved = bool(sub)

    try:
        public_test_cases = json.loads(p['public_test_cases'])
    except Exception:
        public_test_cases = []

    try:
        hidden_count = len(json.loads(p['hidden_test_cases']))
    except Exception:
        hidden_count = 0

    starter_codes = get_problem_starter_codes(dict(p))

    return jsonify({
        'problem': {
            'id': p['id'],
            'title': p['title'],
            'slug': p['slug'],
            'difficulty': p['difficulty'],
            'category': p['category'],
            'description': p['description'],
            'starter_code': starter_codes.get('python', p['starter_code']),
            'starter_codes': starter_codes,
            'sample_input': p['sample_input'],
            'sample_output': p['sample_output'],
            'public_test_cases': public_test_cases,
            'hidden_test_cases_count': hidden_count,
            'is_solved': is_solved
        }
    }), 200


def normalize_output(val_str: str):
    """Normalizes output strings into typed primitives for comparison."""
    if val_str is None:
        return None
    s = val_str.strip()
    if s.lower() == 'true':
        return True
    if s.lower() == 'false':
        return False
    if (s.startswith('[') and s.endswith(']')) or (s.startswith('{') and s.endswith('}')):
        try:
            return json.loads(s)
        except Exception:
            pass
    try:
        if '.' in s:
            return float(s)
        return int(s)
    except Exception:
        pass
    return s


def run_python_tests(code: str, public_cases: list, hidden_cases: list):
    """Executes Python code against public and hidden test cases."""
    local_scope = {}
    try:
        byte_code = compile(code, '<user_code>', 'exec')
        exec(byte_code, {}, local_scope)

        func = None
        standalone_funcs = [f for f in local_scope.values() if callable(f) and not isinstance(f, type)]
        if standalone_funcs:
            func = standalone_funcs[0]
        else:
            classes = [c for c in local_scope.values() if isinstance(c, type)]
            for cls in classes:
                try:
                    inst = cls()
                    methods = [getattr(inst, m) for m in dir(inst) if callable(getattr(inst, m)) and not m.startswith('__')]
                    if methods:
                        func = methods[0]
                        break
                except Exception:
                    pass

        if not func:
            return False, False, False, [], "No callable function or Solution method defined in code. Define a function (e.g. def solution(...):) or class Solution.", 400

        test_results = []
        all_public_passed = True
        all_hidden_passed = True

        for idx, tc in enumerate(public_cases, 1):
            inputs = tc.get('input', {})
            expected = tc.get('expected')
            try:
                if isinstance(inputs, dict):
                    actual = func(**inputs)
                elif isinstance(inputs, list):
                    actual = func(*inputs)
                else:
                    actual = func(inputs)

                passed = (actual == expected)
                if not passed:
                    all_public_passed = False

                test_results.append({
                    'case': idx,
                    'is_hidden': False,
                    'passed': passed,
                    'input': str(inputs),
                    'expected': str(expected),
                    'actual': str(actual)
                })
            except Exception as test_err:
                all_public_passed = False
                test_results.append({
                    'case': idx,
                    'is_hidden': False,
                    'passed': False,
                    'input': str(inputs),
                    'expected': str(expected),
                    'error': str(test_err)
                })

        hidden_start_index = len(public_cases) + 1
        for idx, tc in enumerate(hidden_cases, hidden_start_index):
            inputs = tc.get('input', {})
            expected = tc.get('expected')
            try:
                if isinstance(inputs, dict):
                    actual = func(**inputs)
                elif isinstance(inputs, list):
                    actual = func(*inputs)
                else:
                    actual = func(inputs)

                passed = (actual == expected)
                if not passed:
                    all_hidden_passed = False

                test_results.append({
                    'case': idx,
                    'is_hidden': True,
                    'passed': passed,
                    'label': f'Hidden Test Case #{idx - len(public_cases)}'
                })
            except Exception:
                all_hidden_passed = False
                test_results.append({
                    'case': idx,
                    'is_hidden': True,
                    'passed': False,
                    'label': f'Hidden Test Case #{idx - len(public_cases)}',
                    'error': 'Runtime exception on hidden test case'
                })

        all_passed = (all_public_passed and all_hidden_passed)
        return all_passed, all_public_passed, all_hidden_passed, test_results, None, 200

    except Exception as syntax_err:
        return False, False, False, [], str(syntax_err), 400


def build_java_harness(slug: str, public_cases: list, hidden_cases: list):
    all_cases = list(enumerate(public_cases, 1)) + list(enumerate(hidden_cases, len(public_cases) + 1))
    invocations = []
    for idx, tc in all_cases:
        inp = tc.get('input', {})
        if 'two-sum' in slug:
            nums = inp.get('nums', [])
            target = inp.get('target', 0)
            nums_str = "new int[]{" + ", ".join(str(x) for x in nums) + "}"
            invocations.append(f"""
        try {{
            int[] res = sol.twoSum({nums_str}, {target});
            System.out.println("CASE:{idx}:ACTUAL:" + java.util.Arrays.toString(res));
        }} catch (Exception e) {{
            System.out.println("CASE:{idx}:ERROR:" + e.getMessage());
        }}""")
        elif 'valid-palindrome' in slug:
            s_val = str(inp.get('s', '')).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            invocations.append(f"""
        try {{
            boolean res = sol.isPalindrome("{s_val}");
            System.out.println("CASE:{idx}:ACTUAL:" + res);
        }} catch (Exception e) {{
            System.out.println("CASE:{idx}:ERROR:" + e.getMessage());
        }}""")
        elif 'reverse-integer' in slug:
            x_val = inp.get('x', 0)
            invocations.append(f"""
        try {{
            int res = sol.reverseInteger({x_val});
            System.out.println("CASE:{idx}:ACTUAL:" + res);
        }} catch (Exception e) {{
            System.out.println("CASE:{idx}:ERROR:" + e.getMessage());
        }}""")
        elif 'maximum-subarray' in slug:
            nums = inp.get('nums', [])
            nums_str = "new int[]{" + ", ".join(str(x) for x in nums) + "}"
            invocations.append(f"""
        try {{
            int res = sol.maxSubArray({nums_str});
            System.out.println("CASE:{idx}:ACTUAL:" + res);
        }} catch (Exception e) {{
            System.out.println("CASE:{idx}:ERROR:" + e.getMessage());
        }}""")
        elif 'valid-parentheses' in slug:
            s_val = str(inp.get('s', '')).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            invocations.append(f"""
        try {{
            boolean res = sol.isValidParentheses("{s_val}");
            System.out.println("CASE:{idx}:ACTUAL:" + res);
        }} catch (Exception e) {{
            try {{
                boolean res2 = sol.isValid("{s_val}");
                System.out.println("CASE:{idx}:ACTUAL:" + res2);
            }} catch (Exception e2) {{
                System.out.println("CASE:{idx}:ERROR:" + e.getMessage());
            }}
        }}""")
        elif 'climbing-stairs' in slug:
            n_val = inp.get('n', 0)
            invocations.append(f"""
        try {{
            int res = sol.climbStairs({n_val});
            System.out.println("CASE:{idx}:ACTUAL:" + res);
        }} catch (Exception e) {{
            System.out.println("CASE:{idx}:ERROR:" + e.getMessage());
        }}""")
        elif 'single-number' in slug:
            nums = inp.get('nums', [])
            nums_str = "new int[]{" + ", ".join(str(x) for x in nums) + "}"
            invocations.append(f"""
        try {{
            int res = sol.singleNumber({nums_str});
            System.out.println("CASE:{idx}:ACTUAL:" + res);
        }} catch (Exception e) {{
            System.out.println("CASE:{idx}:ERROR:" + e.getMessage());
        }}""")
        else:
            invocations.append(f"""
        try {{
            java.lang.reflect.Method m = Solution.class.getDeclaredMethods()[0];
            m.setAccessible(true);
            Object res = m.invoke(sol);
            System.out.println("CASE:{idx}:ACTUAL:" + String.valueOf(res));
        }} catch (Exception e) {{
            System.out.println("CASE:{idx}:ERROR:" + e.getMessage());
        }}""")

    invocations_body = "\n".join(invocations)
    return f"""import java.util.*;

public class TestHarness {{
    public static void main(String[] args) {{
        Solution sol = new Solution();
{invocations_body}
    }}
}}
"""


def run_java_tests(code: str, slug: str, public_cases: list, hidden_cases: list):
    """Compiles and executes Java code against test cases."""
    javac_bin = shutil.which('javac') or r'C:\Program Files\Common Files\Oracle\Java\javapath\javac.EXE'
    java_bin = shutil.which('java') or r'C:\Program Files\Common Files\Oracle\Java\javapath\java.EXE'

    if not os.path.exists(javac_bin) and not shutil.which('javac'):
        return False, False, False, [], "Java compiler (javac) not found on system PATH. Please install OpenJDK or run via Docker.", 400

    harness_code = build_java_harness(slug, public_cases, hidden_cases)

    with tempfile.TemporaryDirectory() as td:
        sol_file = os.path.join(td, 'Solution.java')
        harness_file = os.path.join(td, 'TestHarness.java')

        cleaned_code = re.sub(r'public\s+class\s+([A-Za-z0-9_]+)', 'public class Solution', code)
        if 'class Solution' not in cleaned_code:
            cleaned_code = f"public class Solution {{\n{cleaned_code}\n}}"

        with open(sol_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_code)
        with open(harness_file, 'w', encoding='utf-8') as f:
            f.write(harness_code)

        comp = subprocess.run([javac_bin, 'Solution.java', 'TestHarness.java'], cwd=td, capture_output=True, text=True)
        if comp.returncode != 0:
            return False, False, False, [], f"Java Compilation Error:\n{comp.stderr}", 400

        try:
            run = subprocess.run([java_bin, 'TestHarness'], cwd=td, capture_output=True, text=True, timeout=6)
        except subprocess.TimeoutExpired:
            return False, False, False, [], "Time Limit Exceeded (5000ms): Your Java solution took too long to execute.", 400

        output_map = {}
        for line in run.stdout.splitlines():
            line = line.strip()
            if line.startswith('CASE:'):
                parts = line.split(':', 3)
                if len(parts) >= 4:
                    case_idx = int(parts[1])
                    status_type = parts[2]
                    val = parts[3]
                    output_map[case_idx] = (status_type, val)

        test_results = []
        all_public_passed = True
        all_hidden_passed = True

        for idx, tc in enumerate(public_cases, 1):
            expected = tc.get('expected')
            status_type, val = output_map.get(idx, ('ERROR', 'No output produced'))
            if status_type == 'ERROR':
                all_public_passed = False
                test_results.append({
                    'case': idx,
                    'is_hidden': False,
                    'passed': False,
                    'input': str(tc.get('input', {})),
                    'expected': str(expected),
                    'error': val
                })
            else:
                actual = normalize_output(val)
                passed = (actual == expected)
                if not passed:
                    all_public_passed = False
                test_results.append({
                    'case': idx,
                    'is_hidden': False,
                    'passed': passed,
                    'input': str(tc.get('input', {})),
                    'expected': str(expected),
                    'actual': str(actual)
                })

        hidden_start = len(public_cases) + 1
        for idx, tc in enumerate(hidden_cases, hidden_start):
            expected = tc.get('expected')
            status_type, val = output_map.get(idx, ('ERROR', 'No output produced'))
            if status_type == 'ERROR':
                all_hidden_passed = False
                test_results.append({
                    'case': idx,
                    'is_hidden': True,
                    'passed': False,
                    'label': f'Hidden Test Case #{idx - len(public_cases)}',
                    'error': 'Runtime exception on hidden test case'
                })
            else:
                actual = normalize_output(val)
                passed = (actual == expected)
                if not passed:
                    all_hidden_passed = False
                test_results.append({
                    'case': idx,
                    'is_hidden': True,
                    'passed': passed,
                    'label': f'Hidden Test Case #{idx - len(public_cases)}'
                })

        all_passed = (all_public_passed and all_hidden_passed)
        return all_passed, all_public_passed, all_hidden_passed, test_results, None, 200


def build_c_cpp_harness(language: str, slug: str, public_cases: list, hidden_cases: list):
    is_cpp = (language in ('cpp', 'c++'))
    all_cases = list(enumerate(public_cases, 1)) + list(enumerate(hidden_cases, len(public_cases) + 1))
    invocations = []

    for idx, tc in all_cases:
        inp = tc.get('input', {})
        if 'two-sum' in slug:
            nums = inp.get('nums', [])
            target = inp.get('target', 0)
            n_len = len(nums)
            nums_str = "{" + ", ".join(str(x) for x in nums) + "}"
            if is_cpp:
                invocations.append(f"""
    {{
        vector<int> nums = {nums_str};
        vector<int> res = sol.twoSum(nums, {target});
        if (res.size() >= 2) {{
            cout << "CASE:{idx}:ACTUAL:[" << res[0] << ", " << res[1] << "]" << endl;
        }} else {{
            cout << "CASE:{idx}:ACTUAL:[]" << endl;
        }}
    }}""")
            else:
                invocations.append(f"""
    {{
        int nums[] = {nums_str};
        int retSize = 0;
        int* res = twoSum(nums, {n_len}, {target}, &retSize);
        if (res != NULL && retSize >= 2) {{
            printf("CASE:{idx}:ACTUAL:[%d, %d]\\n", res[0], res[1]);
            free(res);
        }} else {{
            printf("CASE:{idx}:ACTUAL:[]\\n");
        }}
    }}""")
        elif 'valid-palindrome' in slug:
            s_val = str(inp.get('s', '')).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            if is_cpp:
                invocations.append(f"""
    {{
        bool res = sol.isPalindrome("{s_val}");
        cout << "CASE:{idx}:ACTUAL:" << (res ? "true" : "false") << endl;
    }}""")
            else:
                invocations.append(f"""
    {{
        bool res = isPalindrome("{s_val}");
        printf("CASE:{idx}:ACTUAL:%s\\n", res ? "true" : "false");
    }}""")
        elif 'reverse-integer' in slug:
            x_val = inp.get('x', 0)
            if is_cpp:
                invocations.append(f"""
    {{
        int res = sol.reverseInteger({x_val});
        cout << "CASE:{idx}:ACTUAL:" << res << endl;
    }}""")
            else:
                invocations.append(f"""
    {{
        int res = reverseInteger({x_val});
        printf("CASE:{idx}:ACTUAL:%d\\n", res);
    }}""")
        elif 'maximum-subarray' in slug:
            nums = inp.get('nums', [])
            n_len = len(nums)
            nums_str = "{" + ", ".join(str(x) for x in nums) + "}"
            if is_cpp:
                invocations.append(f"""
    {{
        vector<int> nums = {nums_str};
        int res = sol.maxSubArray(nums);
        cout << "CASE:{idx}:ACTUAL:" << res << endl;
    }}""")
            else:
                invocations.append(f"""
    {{
        int nums[] = {nums_str};
        int res = maxSubArray(nums, {n_len});
        printf("CASE:{idx}:ACTUAL:%d\\n", res);
    }}""")
        elif 'valid-parentheses' in slug:
            s_val = str(inp.get('s', '')).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            if is_cpp:
                invocations.append(f"""
    {{
        bool res = sol.isValidParentheses("{s_val}");
        cout << "CASE:{idx}:ACTUAL:" << (res ? "true" : "false") << endl;
    }}""")
            else:
                invocations.append(f"""
    {{
        bool res = isValidParentheses("{s_val}");
        printf("CASE:{idx}:ACTUAL:%s\\n", res ? "true" : "false");
    }}""")
        elif 'climbing-stairs' in slug:
            n_val = inp.get('n', 0)
            if is_cpp:
                invocations.append(f"""
    {{
        int res = sol.climbStairs({n_val});
        cout << "CASE:{idx}:ACTUAL:" << res << endl;
    }}""")
            else:
                invocations.append(f"""
    {{
        int res = climbStairs({n_val});
        printf("CASE:{idx}:ACTUAL:%d\\n", res);
    }}""")
        elif 'single-number' in slug:
            nums = inp.get('nums', [])
            n_len = len(nums)
            nums_str = "{" + ", ".join(str(x) for x in nums) + "}"
            if is_cpp:
                invocations.append(f"""
    {{
        vector<int> nums = {nums_str};
        int res = sol.singleNumber(nums);
        cout << "CASE:{idx}:ACTUAL:" << res << endl;
    }}""")
            else:
                invocations.append(f"""
    {{
        int nums[] = {nums_str};
        int res = singleNumber(nums, {n_len});
        printf("CASE:{idx}:ACTUAL:%d\\n", res);
    }}""")

    invocations_body = "\n".join(invocations)
    if is_cpp:
        return f"""#include <iostream>
#include <vector>
#include <string>
using namespace std;

int main() {{
    Solution sol;
{invocations_body}
    return 0;
}}
"""
    else:
        return f"""#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

int main() {{
{invocations_body}
    return 0;
}}
"""


def run_c_cpp_tests(language: str, code: str, slug: str, public_cases: list, hidden_cases: list):
    """Compiles and runs C or C++ code using GCC / G++."""
    compiler = 'gcc' if language == 'c' else 'g++'
    compiler_bin = shutil.which(compiler)
    if not compiler_bin:
        return False, False, False, [], (
            f"{compiler.upper()} compiler not found on system PATH. "
            f"To execute {language.upper()} solutions locally on Windows, install MinGW-w64 GCC, "
            f"or run Code Everyday using the included Docker container (docker compose up)."
        ), 400

    harness_code = build_c_cpp_harness(language, slug, public_cases, hidden_cases)
    with tempfile.TemporaryDirectory() as td:
        ext = 'c' if language == 'c' else 'cpp'
        sol_file = os.path.join(td, f'solution.{ext}')
        harness_file = os.path.join(td, f'harness.{ext}')
        out_bin = os.path.join(td, 'solution.exe' if os.name == 'nt' else 'solution')

        with open(sol_file, 'w', encoding='utf-8') as f:
            f.write(code)
        with open(harness_file, 'w', encoding='utf-8') as f:
            f.write(harness_code)

        comp = subprocess.run([compiler_bin, '-O2', sol_file, harness_file, '-o', out_bin], cwd=td, capture_output=True, text=True)
        if comp.returncode != 0:
            return False, False, False, [], f"{language.upper()} Compilation Error:\n{comp.stderr}", 400

        try:
            run = subprocess.run([out_bin], cwd=td, capture_output=True, text=True, timeout=5)
        except subprocess.TimeoutExpired:
            return False, False, False, [], f"Time Limit Exceeded (5000ms): Your {language.upper()} solution took too long to execute.", 400

        output_map = {}
        for line in run.stdout.splitlines():
            line = line.strip()
            if line.startswith('CASE:'):
                parts = line.split(':', 3)
                if len(parts) >= 4:
                    case_idx = int(parts[1])
                    val = parts[3]
                    output_map[case_idx] = val

        test_results = []
        all_public_passed = True
        all_hidden_passed = True

        for idx, tc in enumerate(public_cases, 1):
            expected = tc.get('expected')
            val = output_map.get(idx, 'No output')
            actual = normalize_output(val)
            passed = (actual == expected)
            if not passed:
                all_public_passed = False
            test_results.append({
                'case': idx,
                'is_hidden': False,
                'passed': passed,
                'input': str(tc.get('input', {})),
                'expected': str(expected),
                'actual': str(actual)
            })

        hidden_start = len(public_cases) + 1
        for idx, tc in enumerate(hidden_cases, hidden_start):
            expected = tc.get('expected')
            val = output_map.get(idx, 'No output')
            actual = normalize_output(val)
            passed = (actual == expected)
            if not passed:
                all_hidden_passed = False
            test_results.append({
                'case': idx,
                'is_hidden': True,
                'passed': passed,
                'label': f'Hidden Test Case #{idx - len(public_cases)}'
            })

        all_passed = (all_public_passed and all_hidden_passed)
        return all_passed, all_public_passed, all_hidden_passed, test_results, None, 200


@app.route('/api/submit-solution', methods=['POST'])
def api_submit_solution():
    """
    Evaluates multilingual code (Python, Java, C, C++) against Public & Secret Hidden Test Cases.
    User's code is ONLY Accepted if all public AND all hidden test cases pass.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required to submit solution.'}), 401

    data = request.get_json() or {}
    problem_id = data.get('problem_id')
    code = data.get('code', '').strip()
    language = (data.get('language') or 'python').lower().strip()
    is_daily = bool(data.get('is_daily', False))

    if not problem_id:
        return jsonify({'error': 'Problem ID is required.'}), 400

    if language not in ('python', 'py', 'java', 'c', 'cpp', 'c++'):
        return jsonify({'error': f'Unsupported language "{language}". Choose python, java, c, or cpp.'}), 400

    with get_db() as conn:
        problem = conn.execute('SELECT * FROM problems WHERE id = ?', (problem_id,)).fetchone()
        if not problem:
            return jsonify({'error': 'Problem not found.'}), 404

    try:
        public_test_cases = json.loads(problem['public_test_cases'])
    except Exception:
        public_test_cases = []

    try:
        hidden_test_cases = json.loads(problem['hidden_test_cases'])
    except Exception:
        hidden_test_cases = []

    # Dispatch to language-specific runner
    if language in ('python', 'py'):
        all_passed, all_public_passed, all_hidden_passed, test_results, err_msg, code_status = run_python_tests(
            code, public_test_cases, hidden_test_cases
        )
    elif language == 'java':
        all_passed, all_public_passed, all_hidden_passed, test_results, err_msg, code_status = run_java_tests(
            code, problem['slug'], public_test_cases, hidden_test_cases
        )
    elif language == 'c':
        all_passed, all_public_passed, all_hidden_passed, test_results, err_msg, code_status = run_c_cpp_tests(
            'c', code, problem['slug'], public_test_cases, hidden_test_cases
        )
    else:  # cpp / c++
        all_passed, all_public_passed, all_hidden_passed, test_results, err_msg, code_status = run_c_cpp_tests(
            'cpp', code, problem['slug'], public_test_cases, hidden_test_cases
        )

    if err_msg:
        return jsonify({
            'success': False,
            'status': 'Error',
            'error': err_msg,
            'language': language
        }), code_status

    submission_status = 'Accepted' if all_passed else 'Wrong Answer'

    # Record in database with language
    with get_db() as conn:
        conn.execute('''
            INSERT INTO user_submissions (user_id, problem_id, status, code, language, is_daily)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, problem_id, submission_status, code, language, 1 if is_daily else 0))
        conn.commit()

    streak_info = None
    if all_passed and is_daily:
        daily_p = get_or_create_daily_problem()
        if daily_p and daily_p['id'] == problem_id:
            new_streak, max_streak, incremented = update_user_streak(user_id)
            streak_info = {
                'current_streak': new_streak,
                'max_streak': max_streak,
                'streak_incremented': incremented
            }

    total_cases = len(test_results)
    passed_cases = sum(1 for t in test_results if t['passed'])

    if all_passed:
        message = f"Accepted! All {total_cases} test cases passed (including secret hidden test cases)! Streak updated!"
    elif not all_public_passed:
        message = f"Failed on public test cases ({passed_cases}/{total_cases} passed). Debug and retry."
    else:
        message = f"Public test cases passed, but failed on secret hidden edge cases ({passed_cases}/{total_cases} passed). Check boundary constraints and corner cases!"

    return jsonify({
        'success': all_passed,
        'status': submission_status,
        'language': language,
        'test_results': test_results,
        'total_cases': total_cases,
        'passed_cases': passed_cases,
        'all_public_passed': all_public_passed,
        'all_hidden_passed': all_hidden_passed,
        'all_passed': all_passed,
        'streak_info': streak_info,
        'message': message
    }), 200


@app.route('/api/user/stats', methods=['GET'])
def api_user_stats():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    with get_db() as conn:
        user = conn.execute('SELECT id, name, email, current_streak, max_streak, last_streak_date, created_at FROM users WHERE id = ?', (user_id,)).fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        solved_total = conn.execute('''
            SELECT COUNT(DISTINCT problem_id) as count
            FROM user_submissions
            WHERE user_id = ? AND status = 'Accepted'
        ''', (user_id,)).fetchone()['count']

        total_problems = conn.execute('SELECT COUNT(*) as count FROM problems').fetchone()['count']

        breakdown = conn.execute('''
            SELECT p.difficulty, COUNT(DISTINCT p.id) as count
            FROM problems p
            JOIN user_submissions s ON p.id = s.problem_id
            WHERE s.user_id = ? AND s.status = 'Accepted'
            GROUP BY p.difficulty
        ''', (user_id,)).fetchall()

        diff_counts = {'Easy': 0, 'Medium': 0, 'Hard': 0}
        for b in breakdown:
            diff_counts[b['difficulty']] = b['count']

        recent = conn.execute('''
            SELECT s.id, s.status, s.language, s.submitted_at, p.title, p.difficulty
            FROM user_submissions s
            JOIN problems p ON s.problem_id = p.id
            WHERE s.user_id = ?
            ORDER BY s.submitted_at DESC
            LIMIT 6
        ''', (user_id,)).fetchall()

    return jsonify({
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'current_streak': user['current_streak'] or 0,
            'max_streak': user['max_streak'] or 0,
            'last_streak_date': user['last_streak_date'] or 'None yet',
            'created_at': user['created_at']
        },
        'stats': {
            'solved_total': solved_total,
            'total_problems': total_problems,
            'easy_solved': diff_counts['Easy'],
            'medium_solved': diff_counts['Medium'],
            'hard_solved': diff_counts['Hard']
        },
        'recent_submissions': [dict(r) for r in recent],
        'has_gemini_key': bool(get_gemini_api_key())
    }), 200


@app.route('/api/settings/gemini-key', methods=['POST'])
def api_set_gemini_key():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json() or {}
    api_key = (data.get('api_key') or '').strip()

    if not api_key:
        return jsonify({'error': 'Please enter a valid API key.'}), 400

    with get_db() as conn:
        conn.execute('''
            INSERT INTO app_settings (key, value)
            VALUES ('gemini_api_key', ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        ''', (api_key,))
        conn.commit()

    return jsonify({
        'success': True,
        'message': 'Gemini 2.5 Flash API key saved! New daily questions will be generated by Gemini.'
    }), 200


@app.route('/api/problems/generate-now', methods=['POST'])
def api_generate_problem_now():
    """Generates a fresh question using Gemini 2.5 Flash right now and inserts it into the problems library."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    api_key = get_gemini_api_key()
    problem_data = generate_question_with_gemini(api_key)
    if not problem_data or not problem_data.get('title'):
        return jsonify({'error': 'Gemini API call failed. Please check key validity and network.'}), 502

    title = problem_data.get('title', 'AI Generated Problem').strip()
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-') + f"-{random.randint(100, 999)}"
    public_cases = json.dumps(problem_data.get('public_test_cases', []))
    hidden_cases = json.dumps(problem_data.get('hidden_test_cases', []))

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO problems (title, slug, difficulty, category, description, starter_code, sample_input, sample_output, public_test_cases, hidden_test_cases)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            title,
            slug,
            problem_data.get('difficulty', 'Medium'),
            problem_data.get('category', 'Algorithms'),
            problem_data.get('description', ''),
            problem_data.get('starter_code', 'def solution():\n    pass'),
            problem_data.get('sample_input', ''),
            problem_data.get('sample_output', ''),
            public_cases,
            hidden_cases
        ))
        conn.commit()
        new_id = cursor.lastrowid

    return jsonify({
        'success': True,
        'message': f'Gemini successfully generated "{title}" with hidden test cases!',
        'problem_id': new_id
    }), 201


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n🚀 Authentication & Coding Dashboard Server running on http://127.0.0.1:{port}\n")
    app.run(host='0.0.0.0', port=port, debug=True)
