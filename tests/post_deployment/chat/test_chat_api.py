"""
Chat API tests for the RAG-LLM Framework post-deployment test suite.
"""
import uuid
from tests.post_deployment.utils.base_test import BaseTest
from tests.post_deployment.utils.config import TEST_CHAT_MESSAGE, TEST_FEEDBACK

class SendChatMessageTest(BaseTest):
    """Test sending a chat message."""
    
    def __init__(self):
        super().__init__(
            name="Chat Send API",
            description="Test sending a message to the chat API."
        )
        self.conversation_id = None
        
    def execute(self):
        data = {"message": TEST_CHAT_MESSAGE}
        success, response = self.request("POST", "/chat/send", data)
        
        if success and "conversation_id" in response:
            self.conversation_id = response["conversation_id"]
            return True
        return False
        
    def get_conversation_id(self):
        """Get the conversation ID from this test."""
        return self.conversation_id or f"test-{str(uuid.uuid4())}"
        
class ChatHistoryTest(BaseTest):
    """Test retrieving chat history."""
    
    def __init__(self, conversation_id=None):
        super().__init__(
            name="Chat History API",
            description="Test retrieving chat history for a conversation."
        )
        self.conversation_id = conversation_id or f"test-{str(uuid.uuid4())}"
        
    def execute(self):
        success, response = self.request("GET", f"/chat/history/{self.conversation_id}")
        return success and "messages" in response
        
class ChatFeedbackTest(BaseTest):
    """Test submitting chat feedback."""
    
    def __init__(self, conversation_id=None):
        super().__init__(
            name="Chat Feedback API",
            description="Test submitting feedback for a chat message."
        )
        self.conversation_id = conversation_id or f"test-{str(uuid.uuid4())}"
        
    def execute(self):
        data = {
            "conversation_id": self.conversation_id,
            "message_idx": 0,
            "feedback": TEST_FEEDBACK,
            "rating": 5,
            "details": "Automated test feedback"
        }
        success, response = self.request("POST", "/chat/feedback", data)
        return success and response.get("status") == "success"

def get_chat_tests():
    send_test = SendChatMessageTest()
    return [
        send_test,
        ChatHistoryTest(send_test.get_conversation_id()),
        ChatFeedbackTest(send_test.get_conversation_id())
    ]
