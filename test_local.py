"""Standard-library smoke tests for local server document and validation routes."""
import io
import unittest
from unittest.mock import patch
from local_server import app

class LocalTests(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_home(self):
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_document_pdf(self):
        response = self.client.post("/api/document", json={"title": "Test", "body": "Hello world", "format": "pdf"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.startswith(b"%PDF"))

    def test_document_word(self):
        response = self.client.post("/api/document", json={"title": "Test", "body": "Hello world", "format": "docx"})
        self.assertEqual(response.status_code, 200)
        from docx import Document
        doc = Document(io.BytesIO(response.data))
        self.assertIn("Hello world", [p.text for p in doc.paragraphs])

    def test_invalid_chat(self):
        self.assertEqual(self.client.post("/api/chat", json={"messages": []}).status_code, 400)

    def test_invalid_image(self):
        self.assertEqual(self.client.post("/api/image", json={"prompt": ""}).status_code, 400)

if __name__ == "__main__":
    unittest.main()
