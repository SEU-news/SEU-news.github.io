"""
Django REST API 测试脚本

快速测试所有 API 端点是否正常工作
"""

import requests
import json


class APITester:
    """API 测试器"""

    def __init__(self, base_url='http://localhost:42611/api'):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

    def print_result(self, test_name, success, message=''):
        """打印测试结果"""
        # Windows GBK 编码不支持表情符号，使用 ASCII 替代
        status = '[PASS]' if success else '[FAIL]'
        print(f"{status} - {test_name}")
        if message:
            print(f"      {message}")
        print()

    def test_health(self):
        """测试服务健康状态"""
        try:
            response = self.session.get(self.base_url)
            # 404 是正常的，因为我们访问的是 /api/ 而不是具体的端点
            success = response.status_code in [200, 404]
            self.print_result('健康检查', success, f'Status: {response.status_code}')
            return success
        except Exception as e:
            self.print_result('健康检查', False, str(e))
            return False

    def test_register(self):
        """测试注册"""
        url = f"{self.base_url}/auth/register/"
        data = {
            'username': 'test_user_api',
            'password': 'test123456',
            'realname': '测试用户',
            'student_id': '123456'
        }

        try:
            response = self.session.post(url, json=data)
            success = response.status_code in [200, 400]  # 400 表示用户已存在
            self.print_result('注册 API', success, f'Status: {response.status_code}')
            return success
        except Exception as e:
            self.print_result('注册 API', False, str(e))
            return False

    def test_login(self):
        """测试登录"""
        url = f"{self.base_url}/auth/login/"
        data = {
            'username': 'admin',
            'password': '123456'
        }

        try:
            response = self.session.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                success = result.get('success', False)
                if success:
                    self.token = self.session.cookies.get('sessionid')
                    user = result['user']
                    perm_info = f'Editor: {user.get("has_editor_perm")}, Admin: {user.get("has_admin_perm")}'
                    self.print_result('登录 API', True, f'User: {user["username"]}, Role: {user["role"]}')
                    print(f"      Permissions: {perm_info}")
                    print()
                    return True

            self.print_result('登录 API', False, f'Status: {response.status_code}, Body: {response.text[:100]}')
            return False
        except Exception as e:
            self.print_result('登录 API', False, str(e))
            return False

    def test_current_user(self):
        """测试获取当前用户"""
        url = f"{self.base_url}/auth/user/"

        try:
            response = self.session.get(url)
            success = response.status_code == 200
            if success:
                result = response.json()
                perm_info = f'Editor: {result.get("has_editor_perm")}, Admin: {result.get("has_admin_perm")}'
                self.print_result('获取当前用户 API', True, f'Username: {result.get("username")}, Role: {result.get("role")}')
                print(f"      Permissions: {perm_info}")
                print()
            else:
                self.print_result('获取当前用户 API', False, f'Status: {response.status_code}')
            return success
        except Exception as e:
            self.print_result('获取当前用户 API', False, str(e))
            return False

    def test_content_list(self):
        """测试内容列表"""
        url = f"{self.base_url}/content/"

        try:
            response = self.session.get(url)
            success = response.status_code == 200
            if success:
                result = response.json()
                self.print_result('内容列表 API', True, f'Count: {result.get("count", 0)}')
            else:
                self.print_result('内容列表 API', False, f'Status: {response.status_code}')
            return success
        except Exception as e:
            self.print_result('内容列表 API', False, str(e))
            return False

    def test_search(self):
        """测试搜索"""
        url = f"{self.base_url}/search/"
        data = {'q': '测试'}

        try:
            response = self.session.post(url, json=data)
            success = response.status_code == 200
            if success:
                result = response.json()
                self.print_result('搜索 API', True, f'Results: {result.get("count", 0)}')
            else:
                self.print_result('搜索 API', False, f'Status: {response.status_code}')
            return success
        except Exception as e:
            self.print_result('搜索 API', False, str(e))
            return False

    def test_logout(self):
        """测试登出"""
        url = f"{self.base_url}/auth/logout/"

        try:
            response = self.session.post(url)
            success = response.status_code == 200
            self.print_result('登出 API', success, f'Status: {response.status_code}')
            return success
        except Exception as e:
            self.print_result('登出 API', False, str(e))
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("  Django REST API 测试")
        print("=" * 60)
        print()

        results = []

        # 测试序列
        results.append(('健康检查', self.test_health()))
        results.append(('注册 API', self.test_register()))
        results.append(('登录 API', self.test_login()))

        # 需要登录的测试
        if self.test_login():
            results.append(('获取当前用户 API', self.test_current_user()))
            results.append(('内容列表 API', self.test_content_list()))
            results.append(('搜索 API', self.test_search()))
            results.append(('登出 API', self.test_logout()))

        # 汇总
        print("=" * 60)
        print("  测试汇总")
        print("=" * 60)
        passed = sum(1 for _, success in results if success)
        total = len(results)

        for test_name, success in results:
            status = '[PASS]' if success else '[FAIL]'
            print(f"{status} {test_name}")

        print()
        print(f"通过: {passed}/{total}")
        print(f"通过率: {passed/total*100:.1f}%")
        print("=" * 60)

        return passed == total


if __name__ == '__main__':
    tester = APITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
