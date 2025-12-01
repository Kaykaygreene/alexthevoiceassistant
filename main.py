import os
import signal

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
from tools import client_tools

load_dotenv()

agent_id = os.getenv("AGENT_ID")
api_key = os.getenv("ELEVENLABS_API_KEY")

print("AGENT_ID:", agent_id)
print("API_KEY:", api_key[:5] + "...")

elevenlabs = ElevenLabs(api_key=api_key)

conversation = Conversation(
    elevenlabs,
    agent_id,
    client_tools=client_tools,
    requires_auth=bool(api_key),
    audio_interface=DefaultAudioInterface(),
    callback_agent_response=lambda response: print(f"Agent: {response}"),
    callback_agent_response_correction=lambda original, corrected: print(f"Agent: {original} -> {corrected}"),
    callback_user_transcript=lambda transcript: print(f"User: {transcript}"),
)

#start the session with NO user_id
conversation.start_session()

# Stop session safely on CTRL+C
signal.signal(signal.SIGINT, lambda sig, frame: conversation.end_session())

conversation_id = conversation.wait_for_session_end()
print(f"Conversation ID: {conversation_id}")
