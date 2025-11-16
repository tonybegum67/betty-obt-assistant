"""
Cassidy AI API Client for Betty.

Provides integration with Cassidy.ai assistant for hybrid AI response mode.
"""

import requests
import os
from typing import Optional, Dict
from pathlib import Path


class CassidyClient:
    """Client for Cassidy.ai Assistant API."""

    BASE_URL = "https://app.cassidyai.com/api"

    def __init__(self, api_key: Optional[str] = None, assistant_id: Optional[str] = None):
        """
        Initialize Cassidy client.

        Args:
            api_key: Cassidy API key (defaults to CASSIDY_API_KEY env var)
            assistant_id: Cassidy assistant ID (defaults to CASSIDY_ASSISTANT_ID env var)
        """
        self.api_key = api_key or os.getenv("CASSIDY_API_KEY")
        self.assistant_id = assistant_id or os.getenv("CASSIDY_ASSISTANT_ID", "cmgjq8s7802e1n70frp8qad4r")

        if not self.api_key:
            raise ValueError(
                "CASSIDY_API_KEY not found. Please set it in .env file or pass it to constructor."
            )

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with API key."""
        return {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

    def create_thread(self) -> Optional[str]:
        """
        Create a new chat thread with the Cassidy assistant.

        Returns:
            thread_id if successful, None otherwise
        """
        url = f"{self.BASE_URL}/assistants/thread/create"
        data = {'assistant_id': self.assistant_id}

        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=data,
                timeout=30
            )

            if response.status_code != 200:
                print(f"❌ Thread creation failed: {response.status_code} - {response.text}")
                return None

            result = response.json()
            thread_id = result.get('thread_id')

            if thread_id:
                print(f"✅ Cassidy thread created: {thread_id}")

            return thread_id

        except Exception as e:
            print(f"❌ Error creating Cassidy thread: {e}")
            return None

    def send_message(self, thread_id: str, message: str) -> Optional[str]:
        """
        Send a message to a Cassidy thread and get the response.

        Args:
            thread_id: The thread ID to send the message to
            message: The user message

        Returns:
            Assistant's response content if successful, None otherwise
        """
        url = f"{self.BASE_URL}/assistants/message/create"
        data = {
            'thread_id': thread_id,
            'message': message
        }

        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=data,
                timeout=60
            )

            if response.status_code != 200:
                print(f"❌ Message send failed: {response.status_code} - {response.text}")
                return None

            result = response.json()
            content = result.get('content')

            return content

        except Exception as e:
            print(f"❌ Error sending message to Cassidy: {e}")
            return None

    def chat(self, message: str, thread_id: Optional[str] = None) -> tuple[Optional[str], Optional[str]]:
        """
        Convenience method: Create thread (if needed) and send message in one call.

        Args:
            message: The user message
            thread_id: Optional existing thread_id (creates new one if None)

        Returns:
            Tuple of (response_content, thread_id)
        """
        # Create thread if not provided
        if not thread_id:
            thread_id = self.create_thread()
            if not thread_id:
                return None, None

        # Send message
        response = self.send_message(thread_id, message)

        return response, thread_id


# Singleton instance for app-wide use
_cassidy_client = None

def get_cassidy_client() -> Optional[CassidyClient]:
    """
    Get or create the singleton Cassidy client instance.

    Returns:
        CassidyClient instance if credentials available, None otherwise
    """
    global _cassidy_client

    if _cassidy_client is None:
        try:
            _cassidy_client = CassidyClient()
        except ValueError:
            # API key not configured
            return None

    return _cassidy_client
