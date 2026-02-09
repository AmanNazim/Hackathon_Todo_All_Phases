#!/usr/bin/env python3
"""
ChatKit Integration Helper Script

This script provides helper functions for setting up ChatKit integrations.
"""

import os
from typing import Dict, Any, Optional


def create_chatkit_session_endpoint() -> str:
    """
    Creates a template for the ChatKit session endpoint.

    Returns:
        A string containing the template code for the session endpoint
    """
    return '''
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()
openai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

@app.post("/api/chatkit/session")
def create_chatkit_session():
    session = openai.chatkit.sessions.create({
        # Add your session configuration here
        # For example:
        # workflow={ "id": os.environ["CHATKIT_WORKFLOW_ID"] },
        # user=device_id,
    })
    return {"client_secret": session.client_secret}
'''


def create_react_component() -> str:
    """
    Creates a template for the React component integration.

    Returns:
        A string containing the template code for the React component
    """
    return '''
import { ChatKit, useChatKit } from '@openai/chatkit-react';

export function MyChat() {
  const { control } = useChatKit({
    api: {
      async getClientSecret(existing) {
        if (existing) {
          // Implement session refresh logic here
          const res = await fetch('/api/chatkit/refresh', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ existing })
          });
          const { client_secret } = await res.json();
          return client_secret;
        }

        // Get new client secret
        const res = await fetch('/api/chatkit/session', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });
        const { client_secret } = await res.json();
        return client_secret;
      },
    },
    // Add theme and customization options here
    theme: {
      colorScheme: "light",
      color: {
        accent: {
          primary: "#2D8CFF",
          level: 2
        }
      },
    },
  });

  return <ChatKit control={control} className="h-[600px] w-[320px]" />;
}
'''


def create_html_script_tag() -> str:
    """
    Creates the HTML script tag for ChatKit.

    Returns:
        A string containing the HTML script tag
    """
    return '''
<!-- Add this to your HTML <head> or where you load scripts -->
<script
  src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
  async
></script>
'''


def create_self_hosted_server() -> str:
    """
    Creates a template for a self-hosted ChatKit server.

    Returns:
        A string containing the template code for a self-hosted server
    """
    return '''
from openai_chatkit import ChatKitServer, Agent, Runner
from openai_chatkit.agents import AgentContext, RunContextWrapper
from openai_chatkit.store import SQLiteStore
from openai_chatkit.file_store import DiskFileStore
from openai_chatkit.widgets import stream_widget, Card, Text
from fastapi import FastAPI, Request
from starlette.responses import StreamingResponse, Response
import os


class MyChatKitServer(ChatKitServer):
    def __init__(self, data_store, file_store=None):
        super().__init__(data_store, file_store)

    # Define your agent
    assistant_agent = Agent[AgentContext](
        model="gpt-4o",
        name="Assistant",
        instructions="You are a helpful assistant",
    )

    async def respond(
        self,
        thread: ThreadMetadata,
        input: UserMessageItem | ClientToolCallOutputItem,
        context: Any,
    ) -> AsyncIterator[Event]:
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )
        result = Runner.run_streamed(
            self.assistant_agent,
            await to_input_item(input, self.to_message_content),
            context=agent_context,
        )
        async for event in stream_agent_response(agent_context, result):
            yield event


# Initialize FastAPI app
app = FastAPI()

# Initialize stores
data_store = SQLiteStore()
file_store = DiskFileStore(data_store)

# Initialize server
server = MyChatKitServer(data_store, file_store)

@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    result = await server.process(await request.body(), {})
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")
'''


def show_quickstart_guide():
    """
    Displays a quick start guide for ChatKit integration.
    """
    print("ChatKit Integration Quick Start Guide")
    print("=" * 40)
    print("\n1. Choose your integration approach:")
    print("   - Recommended: OpenAI-hosted backend")
    print("   - Advanced: Self-hosted backend")
    print("\n2. For OpenAI-hosted approach:")
    print("   a. Create an agent workflow using Agent Builder")
    print("   b. Set up the session endpoint (use create_chatkit_session_endpoint())")
    print("   c. Add the ChatKit script to your HTML (use create_html_script_tag())")
    print("   d. Implement the React component (use create_react_component())")
    print("\n3. For self-hosted approach:")
    print("   a. Install the Python SDK: pip install openai-chatkit")
    print("   b. Implement your server (use create_self_hosted_server())")
    print("   c. Deploy your server and connect to the frontend")
    print("\n4. Customize the UI using theming options")
    print("5. Add widgets for interactive experiences")
    print("6. Implement actions for user interactions")
    print("\nRemember to set your OPENAI_API_KEY environment variable!")
    print("Also set CHATKIT_WORKFLOW_ID if using the OpenAI-hosted approach.")
'''


def main():
    """
    Main function to demonstrate the ChatKit helper functions.
    """
    print("ChatKit Integration Helper")
    print("=" * 25)

    while True:
        print("\nOptions:")
        print("1. Show quick start guide")
        print("2. Generate session endpoint code")
        print("3. Generate React component code")
        print("4. Generate HTML script tag")
        print("5. Generate self-hosted server code")
        print("6. Exit")

        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == "1":
            show_quickstart_guide()
        elif choice == "2":
            print("\nSession Endpoint Code:")
            print("-" * 20)
            print(create_chatkit_session_endpoint())
        elif choice == "3":
            print("\nReact Component Code:")
            print("-" * 20)
            print(create_react_component())
        elif choice == "4":
            print("\nHTML Script Tag:")
            print("-" * 15)
            print(create_html_script_tag())
        elif choice == "5":
            print("\nSelf-Hosted Server Code:")
            print("-" * 25)
            print(create_self_hosted_server())
        elif choice == "6":
            print("\nExiting...")
            break
        else:
            print("\nInvalid choice. Please try again.")


if __name__ == "__main__":
    main()