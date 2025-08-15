"""
Quick demo: Creating a simple custom backend in under 50 lines.

This demonstrates how easy it is to extend the MCP server with new backends.
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime

# Import the base backend class
import sys
import os
sys.path.append(os.path.dirname(__file__))

from backends.base_backend import ModelBackend, ModelStatus, InferenceType

logger = logging.getLogger(__name__)


class EchoBackend(ModelBackend):
    """
    Simple echo backend that just echoes back the input.
    Demonstrates the minimal implementation needed for a custom backend.
    """
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        super().__init__(model_id, config)
        self.prefix = config.get("prefix", "Echo: ")
    
    async def initialize(self) -> None:
        """Initialize the echo backend."""
        logger.info(f"Initializing echo backend: {self.model_id}")
        # No real initialization needed for echo
        self._update_status(ModelStatus.AVAILABLE)
        self._initialized = True
    
    async def health_check(self) -> bool:
        """Always healthy for echo backend."""
        self._last_health_check = datetime.utcnow()
        return True
    
    async def shutdown(self) -> None:
        """Shutdown the echo backend."""
        logger.info(f"Shutting down echo backend: {self.model_id}")
        self._update_status(ModelStatus.MAINTENANCE)
        self._initialized = False
    
    def get_capabilities(self) -> List[InferenceType]:
        """Echo backend supports completion and chat."""
        return [InferenceType.COMPLETION, InferenceType.CHAT]
    
    async def generate_completion(self, prompt: str, **kwargs) -> str:
        """Echo the prompt back with prefix."""
        return f"{self.prefix}{prompt}"
    
    async def generate_chat_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Echo the last message content back."""
        if messages:
            last_message = messages[-1].get("content", "")
            return f"{self.prefix}{last_message}"
        return f"{self.prefix}No messages provided"


async def demo_custom_backend():
    """Demonstrate the custom echo backend."""
    print("🎭 Custom Backend Demo: Echo Backend")
    print("=" * 40)
    
    # Create and configure the echo backend
    config = {
        "prefix": "🔄 Echo Response: ",
        "timeout": 30
    }
    
    echo_backend = EchoBackend("demo-echo", config)
    
    try:
        # Initialize
        print("🔧 Initializing echo backend...")
        await echo_backend.initialize()
        print(f"✅ Status: {echo_backend.status}")
        
        # Health check
        print("\n❤️  Testing health check...")
        healthy = await echo_backend.health_check()
        print(f"✅ Health: {'OK' if healthy else 'FAIL'}")
        
        # Test completion
        print("\n💬 Testing completion...")
        prompt = "Hello, world!"
        result = await echo_backend.generate_completion(prompt)
        print(f"📝 Input: {prompt}")
        print(f"🔄 Output: {result}")
        
        # Test chat
        print("\n💭 Testing chat...")
        messages = [
            {"role": "user", "content": "What's the weather like?"},
            {"role": "assistant", "content": "I'm an echo bot, I can't check weather."},
            {"role": "user", "content": "Just echo this message!"}
        ]
        chat_result = await echo_backend.generate_chat_response(messages)
        print(f"💬 Last message: {messages[-1]['content']}")
        print(f"🔄 Echo response: {chat_result}")
        
        # Show backend info
        print("\n📊 Backend Information:")
        info = echo_backend.get_model_info()
        for key, value in info.items():
            if key != "config":  # Skip config details
                print(f"   {key}: {value}")
        
        print("\n🎉 Echo backend demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        
    finally:
        # Clean up
        await echo_backend.shutdown()
        print("🧹 Backend shutdown complete")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    # Run the demo
    asyncio.run(demo_custom_backend())
    
    print("\n📚 Next Steps:")
    print("1. Check out docs/mcp-backend-extension-guide.md for detailed instructions")
    print("2. Look at backends/ollama_backend.py for a complete implementation")
    print("3. See examples/openai_compatible_backend.py for API integration")
    print("4. Run test_extensibility.py to validate the system")
    print("\n✨ Creating custom backends is this easy!")