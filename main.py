import os
from dotenv import load_dotenv
from agent import Agent

def main():
    load_dotenv()
    
    # Ensure keys are loaded
    if not os.environ.get("OPENAI_API_KEY") or not os.environ.get("TAVILY_API_KEY"):
        print("Error: Please set OPENAI_API_KEY and TAVILY_API_KEY in your .env file.")
        return

    # Initialize the same General-Purpose ReAct Agent instance for all 3 tasks
    # as strictly required by the constraint in the assignment.
    print("Initializing General-Purpose ReAct Agent...\n")
    agent = Agent()
    
    # Task 1: Planning & Quantitative Reasoning
    task1_query = "What fraction of Japan's population is Taiwan's population as of 2025?"
    print(f"\n--- [Running Task 1: Planning & Quantitative Reasoning] ---")
    agent.execute(task1_query)
    
    # Clear history between tasks so they are evaluated independently
    # Note: the assignment says "use the SAME ReActAgent instance". We just reset conversation history.
    agent.messages = [{"role": "system", "content": agent.system}]
    
    # Task 2: Technical Specificity
    task2_query = "Compare the main display specs of iPhone 15 and Samsung S24."
    print(f"\n\n--- [Running Task 2: Technical Specificity] ---")
    agent.execute(task2_query)
    
    # Clear history
    agent.messages = [{"role": "system", "content": agent.system}]
    
    # Task 3: Resilience & Reflection Test
    task3_query = "Who is the CEO of the startup 'Morphic' AI search?"
    print(f"\n\n--- [Running Task 3: Resilience & Reflection Test] ---")
    agent.execute(task3_query)

if __name__ == "__main__":
    main()
