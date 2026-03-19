import os
from dotenv import load_dotenv
from agent import Agent

def main():
    load_dotenv()
    
    # Ensure keys are loaded
    if not os.environ.get("OPENAI_API_KEY") or not os.environ.get("TAVILY_API_KEY"):
        print("Error: Please set OPENAI_API_KEY and TAVILY_API_KEY in your .env file.")
        return

    print("=============================================")
    print("🤖 Welcome to your Custom ReAct AI Agent!")
    print("Type your question below, or type 'quit' to exit.")
    print("=============================================")
    
    agent = Agent()
    
    while True:
        try:
            user_query = input("\n👉 You: ")
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
                
            if not user_query.strip():
                continue
                
            print("\n--- [Agent is Thinking...] ---")
            answer = agent.execute(user_query)
            
            # Clear the conversation history so it starts fresh for the next question
            agent.messages = [{"role": "system", "content": agent.system}]
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
