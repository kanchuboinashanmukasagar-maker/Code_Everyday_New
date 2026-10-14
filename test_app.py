"""
Test Suite for Code Everyday • Daily Coding & Streak Platform
Tests rebranding, starter stubs (no solutions), multilingual execution (Python, Java, C, C++),
hidden test cases secrecy & gating, and daily streak engine.
"""

import unittest
import json
import os
import re
import shutil
from datetime import datetime, timedelta
from app import app, init_db, get_db

class CodeEverydayTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_01_rebranding_verified(self):
        """Verifies 'Code Everyday' branding across index and dashboard, and absence of old branding."""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Code Everyday", res.data)
        self.assertNotIn(b"Nexus Auth Pro", res.data)
        self.assertNotIn(b"Account Portal", res.data)

        # Login and check dashboard
        self.client.post('/api/auth/login', json={
            'email': 'alex.taylor@example.com',
            'password': 'ApexGuard#2026!'
        })
        dash_res = self.client.get('/dashboard')
        self.assertEqual(dash_res.status_code, 200)
        self.assertIn(b"Code Everyday", dash_res.data)
        self.assertNotIn(b"Nexus Auth Pro", dash_res.data)
        self.assertNotIn(b"Account Portal", dash_res.data)

    def test_02_login_and_access_dashboard(self):
        login_res = self.client.post('/api/auth/login', json={
            'email': 'alex.taylor@example.com',
            'password': 'ApexGuard#2026!'
        })
        self.assertEqual(login_res.status_code, 200)

        dash_res = self.client.get('/dashboard')
        self.assertEqual(dash_res.status_code, 200)
        self.assertIn(b"Today's Question", dash_res.data)
        self.assertIn(b"Practice Problems", dash_res.data)
        self.assertIn(b"Profile", dash_res.data)

    def test_03_daily_problem_has_multilingual_starter_codes_no_solutions(self):
        """Verifies daily problem returns starter stubs with NO working solutions."""
        self.client.post('/api/auth/login', json={
            'email': 'alex.taylor@example.com',
            'password': 'ApexGuard#2026!'
        })

        res = self.client.get('/api/daily-problem')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('problem', data)
        prob = data['problem']
        self.assertIn('starter_codes', prob)
        self.assertIn('python', prob['starter_codes'])
        self.assertIn('java', prob['starter_codes'])
        self.assertIn('c', prob['starter_codes'])
        self.assertIn('cpp', prob['starter_codes'])

        # Python starter stub must be empty/unsolved (pass / # Write your solution)
        py_code = prob['starter_codes']['python']
        self.assertIn('pass', py_code)
        self.assertNotIn('return [i, j]', py_code)
        self.assertNotIn('return max_sum', py_code)

    def test_04_problems_bank_api_and_clean_stubs(self):
        """Verifies all seeded problems have starter codes without solutions."""
        res = self.client.get('/api/problems')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('problems', data)
        self.assertGreaterEqual(len(data['problems']), 7)

        for p in data['problems']:
            detail = self.client.get(f"/api/problems/{p['id']}").get_json()['problem']
            self.assertIn('starter_codes', detail)
            # Python starter stub should not contain reference solutions
            py_code = detail['starter_codes']['python']
            self.assertIn('pass', py_code)

    def test_05_python_solution_evaluation(self):
        """Tests that submitting user-written Python code passes or fails accurately."""
        self.client.post('/api/auth/login', json={
            'email': 'alex.taylor@example.com',
            'password': 'ApexGuard#2026!'
        })

        daily_res = self.client.get('/api/daily-problem')
        daily_data = daily_res.get_json()
        prob_id = daily_data['problem']['id']
        slug = daily_data['problem'].get('slug', '')

        # 1. Submitting empty starter code fails
        empty_res = self.client.post('/api/submit-solution', json={
            'problem_id': prob_id,
            'code': daily_data['problem']['starter_code'],
            'language': 'python',
            'is_daily': False
        })
        self.assertEqual(empty_res.status_code, 200)
        self.assertFalse(empty_res.get_json()['all_passed'])

        # 2. Submitting correct solution for Two Sum (or problem 1)
        two_sum_code = """
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []
"""
        two_sum_res = self.client.post('/api/submit-solution', json={
            'problem_id': 1,
            'code': two_sum_code,
            'language': 'python',
            'is_daily': False
        })
        self.assertEqual(two_sum_res.status_code, 200)
        data = two_sum_res.get_json()
        self.assertTrue(data['all_passed'])
        self.assertEqual(data['status'], 'Accepted')

    def test_06_java_solution_evaluation(self):
        """Tests Java compilation and test execution if javac is available on host."""
        javac = shutil.which('javac') or os.path.exists(r'C:\Program Files\Common Files\Oracle\Java\javapath\javac.EXE')
        if not javac:
            self.skipTest("Java compiler not found in host environment.")

        self.client.post('/api/auth/login', json={
            'email': 'alex.taylor@example.com',
            'password': 'ApexGuard#2026!'
        })

        correct_java_code = """
import java.util.*;

public class Solution {
    public int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int comp = target - nums[i];
            if (map.containsKey(comp)) {
                return new int[] { map.get(comp), i };
            }
            map.put(nums[i], i);
        }
        return new int[0];
    }
}
"""
        res = self.client.post('/api/submit-solution', json={
            'problem_id': 1,
            'code': correct_java_code,
            'language': 'java',
            'is_daily': False
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['all_passed'])
        self.assertEqual(data['status'], 'Accepted')

        # Test incorrect Java solution
        wrong_java_code = """
public class Solution {
    public int[] twoSum(int[] nums, int target) {
        return new int[] { 999, 999 };
    }
}
"""
        wrong_res = self.client.post('/api/submit-solution', json={
            'problem_id': 1,
            'code': wrong_java_code,
            'language': 'java',
            'is_daily': False
        })
        self.assertEqual(wrong_res.status_code, 200)
        wrong_data = wrong_res.get_json()
        self.assertFalse(wrong_data['all_passed'])
        self.assertEqual(wrong_data['status'], 'Wrong Answer')

    def test_07_c_cpp_submission_handling(self):
        """Verifies C / C++ submissions trigger runner and give clear message if compiler missing or compiled."""
        self.client.post('/api/auth/login', json={
            'email': 'alex.taylor@example.com',
            'password': 'ApexGuard#2026!'
        })

        c_code = """
#include <stdlib.h>
int* twoSum(int* nums, int numsSize, int target, int* returnSize) {
    *returnSize = 2;
    int* res = (int*)malloc(2 * sizeof(int));
    for (int i = 0; i < numsSize; i++) {
        for (int j = i + 1; j < numsSize; j++) {
            if (nums[i] + nums[j] == target) {
                res[0] = i; res[1] = j;
                return res;
            }
        }
    }
    return res;
}
"""
        res = self.client.post('/api/submit-solution', json={
            'problem_id': 1,
            'code': c_code,
            'language': 'c',
            'is_daily': False
        })

        if shutil.which('gcc'):
            self.assertEqual(res.status_code, 200)
            self.assertTrue(res.get_json()['all_passed'])
        else:
            self.assertEqual(res.status_code, 400)
            self.assertIn("compiler not found", res.get_json()['error'])

    def test_08_gemini_key_setting(self):
        self.client.post('/api/auth/login', json={
            'email': 'alex.taylor@example.com',
            'password': 'ApexGuard#2026!'
        })

        res = self.client.post('/api/settings/gemini-key', json={
            'api_key': 'AIzaSy_demo_test_key_12345'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])

        stats = self.client.get('/api/user/stats').get_json()
        self.assertTrue(stats['has_gemini_key'])

        from app import DEFAULT_GEMINI_API_KEY
        self.client.post('/api/settings/gemini-key', json={
            'api_key': DEFAULT_GEMINI_API_KEY
        })

    def test_09_user_stats_breakdown_and_languages(self):
        self.client.post('/api/auth/login', json={
            'email': 'alex.taylor@example.com',
            'password': 'ApexGuard#2026!'
        })

        res = self.client.get('/api/user/stats')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('user', data)
        self.assertIn('stats', data)
        self.assertIn('easy_solved', data['stats'])
        self.assertIn('recent_submissions', data)
        if len(data['recent_submissions']) > 0:
            self.assertIn('language', data['recent_submissions'][0])

    def test_10_hidden_test_cases_secrecy(self):
        self.client.post('/api/auth/login', json={
            'email': 'alex.taylor@example.com',
            'password': 'ApexGuard#2026!'
        })

        # 1. Daily problem endpoint
        res = self.client.get('/api/daily-problem')
        self.assertEqual(res.status_code, 200)
        prob = res.get_json()['problem']
        self.assertNotIn('hidden_test_cases', prob)
        self.assertIn('hidden_test_cases_count', prob)
        self.assertGreater(prob['hidden_test_cases_count'], 0)

        # 2. Problem detail endpoint
        detail_res = self.client.get(f'/api/problems/{prob["id"]}')
        self.assertEqual(detail_res.status_code, 200)
        detail_prob = detail_res.get_json()['problem']
        self.assertNotIn('hidden_test_cases', detail_prob)
        self.assertIn('hidden_test_cases_count', detail_prob)

    def test_11_hidden_test_failure_rejects_and_preserves_streak(self):
        self.client.post('/api/auth/login', json={
            'email': 'alex.taylor@example.com',
            'password': 'ApexGuard#2026!'
        })

        daily_data = self.client.get('/api/daily-problem').get_json()
        prob_id = daily_data['problem']['id']

        stats_before = self.client.get('/api/user/stats').get_json()
        streak_before = stats_before['user']['current_streak']

        # Code that only hardcodes public test cases and fails hidden edge cases
        func_match = re.search(r'def\s+([a-zA-Z0-9_]+)\s*\((.*?)\):', daily_data['problem']['starter_code'])
        name = func_match.group(1) if func_match else 'solution'
        params = func_match.group(2) if func_match else '*args, **kwargs'

        code_lines = [f"def {name}({params}):"]
        for tc in daily_data['problem']['public_test_cases']:
            conditions = [f"{k} == {repr(v)}" for k, v in tc['input'].items()]
            cond_str = " and ".join(conditions)
            code_lines.append(f"    if {cond_str}: return {repr(tc['expected'])}")
        code_lines.append("    return -99999999")

        cheating_code = "\n".join(code_lines)
        submit_res = self.client.post('/api/submit-solution', json={
            'problem_id': prob_id,
            'code': cheating_code,
            'language': 'python',
            'is_daily': True
        })
        self.assertEqual(submit_res.status_code, 200)
        data = submit_res.get_json()

        self.assertTrue(data['all_public_passed'])
        self.assertFalse(data['all_hidden_passed'])
        self.assertFalse(data['all_passed'])
        self.assertEqual(data['status'], 'Wrong Answer')
        self.assertIsNone(data['streak_info'])

        for tc in data['test_results']:
            if tc.get('is_hidden'):
                self.assertNotIn('input', tc)
                self.assertNotIn('expected', tc)

        stats_after = self.client.get('/api/user/stats').get_json()
        self.assertEqual(stats_after['user']['current_streak'], streak_before)

    def test_12_shared_daily_question_for_all_users(self):
        # User 1
        self.client.post('/api/auth/login', json={
            'email': 'alex.taylor@example.com',
            'password': 'ApexGuard#2026!'
        })
        user1_daily = self.client.get('/api/daily-problem').get_json()

        # User 2
        self.client.post('/api/auth/login', json={
            'email': 'sarah.connor@example.com',
            'password': 'Password#2026!'
        })
        user2_daily = self.client.get('/api/daily-problem').get_json()

        self.assertEqual(user1_daily['problem']['id'], user2_daily['problem']['id'])
        self.assertEqual(user1_daily['problem']['title'], user2_daily['problem']['title'])
        self.assertEqual(user1_daily['assigned_date'], user2_daily['assigned_date'])


if __name__ == '__main__':
    unittest.main()

