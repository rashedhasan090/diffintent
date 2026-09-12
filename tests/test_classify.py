import unittest

from diffintent.classify import classify_path


class ClassifyTests(unittest.TestCase):
    def test_code(self):
        self.assertEqual(classify_path("src/app.py"), "code")

    def test_tests(self):
        self.assertEqual(classify_path("tests/test_app.py"), "tests")
        self.assertEqual(classify_path("pkg/foo_test.py"), "tests")

    def test_docs(self):
        self.assertEqual(classify_path("README.md"), "docs")
        self.assertEqual(classify_path("docs/guide.rst"), "docs")

    def test_deps(self):
        self.assertEqual(classify_path("requirements.txt"), "deps")
        self.assertEqual(classify_path("package-lock.json"), "deps")

    def test_ci(self):
        self.assertEqual(classify_path(".github/workflows/ci.yml"), "ci")

    def test_config(self):
        self.assertEqual(classify_path(".env.example"), "config")
        self.assertEqual(classify_path("Dockerfile"), "config")

    def test_generated(self):
        self.assertEqual(classify_path("dist/bundle.min.js"), "generated")
        self.assertEqual(classify_path("api_pb2.py"), "generated")


if __name__ == "__main__":
    unittest.main()
