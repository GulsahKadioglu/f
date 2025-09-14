# -*- coding: utf-8 -*-
"""locustfile.py

This file defines a simple load test for the FastAPI backend using Locust.
It simulates user behavior by logging in and making requests to protected
endpoints.

Purpose:
- To perform basic load testing on the application's API.
- To identify performance bottlenecks and measure response times under load.

Key Components:
- `WebsiteUser`: A Locust `HttpUser` class that defines the behavior of a
  simulated user.
- `on_start`: A special Locust method that is called when a user is started.
  It's used here to log in and get an authentication token.
- `@task`: A decorator that marks methods as tasks to be executed by the
  simulated users.
"""

from locust import HttpUser, between, task

from backend.tests.conftest import TEST_USER_PASSWORD


class WebsiteUser(HttpUser):
    """A Locust user class that simulates a user browsing the website.

    This user logs in at the start of the test and then repeatedly makes
    requests to the `/users/me` and `/reports/` endpoints.
    """
    wait_time = between(1, 2)  # Users will wait between 1 and 2 seconds between tasks

    host = "http://localhost:8000"  # Replace with your FastAPI backend URL

    _token = None

    def on_start(self):
        """Called when a Locust user is spawned. Used to log in."""
        self.login()

    def login(self):
        """Logs in a user and saves the access token."""
        response = self.client.post(
            "/api/v1/login/access-token",
            data={
                "username": "test@example.com",  # Replace with a valid test user email
                "password": TEST_USER_PASSWORD,  # Replace with the test user's password
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            name="/login/access-token",
        )
        if response.status_code == 200:
            self._token = response.json()["access_token"]
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            self._token = None

    @task(3)
    def get_users_me(self):
        """Task to get the current user's profile."""
        if self._token:
            self.client.get(
                "/api/v1/users/me",
                headers={"Authorization": f"Bearer {self._token}"},
                name="/users/me",
            )

    @task(1)
    def get_reports(self):
        """Task to get a list of reports."""
        if self._token:
            self.client.get(
                "/api/v1/reports/",
                headers={"Authorization": f"Bearer {self._token}"},
                name="/reports/",
            )
