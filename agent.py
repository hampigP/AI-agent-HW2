import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from tools import search

load_dotenv()

# Define the System Prompt with a strict Few-Shot Example to enforce the ReAct pattern.
REACT_SYSTEM_PROMPT = """You are a ReAct (Reasoning and Acting) Agent. You are designed to answer user queries by interlacing thoughts, actions (tool use), and observations.

You must strictly follow this exact format for EVERY step of your reasoning process:

Thought: [Your step-by-step reasoning about what you need to do next based on the user's query or the latest observation.]
Action: Search["[search_query]"]
Pause

The user will then return the `Observation: [results of the search]`.
You will then start again with a Thought. 

When you have gathered enough information from the observations to fully answer the user's question, output your final answer directly in this format:

Thought: [I now have enough information to form the final answer.]
Action: Finish["[your comprehensive and final answer]"]
Pause

# Critical Tool Instructions:
- You have ONLY ONE tool available: `Search`.
- The format for calling the tool MUST be EXACTLY: Action: Search["your exact query string here"]
- DO NOT hallucinate the Observation. Always output "Pause" immediately after your "Action" line.
- If a search returns no results or irrelevant results, your next Thought MUST reflect on this failure and your next Action MUST try a different, broader, or more specific search query.

# Few-Shot Example:
User: "What is the capital of France and what is its population?"
Thought: I need to find the capital of France first, and then I will search for its population. I should search for "capital of France".
Action: Search["capital of France"]
Pause
Observation: Result 1: Paris is the capital and most populous city of France.
Thought: The capital is Paris. Now I need to find the population of Paris.
Action: Search["population of Paris 2024"]
Pause
Observation: Result 1: The population of Paris as of January 2024 is estimated at 2,102,650 residents.
Thought: I now know the capital is Paris and the population is approximately 2.1 million. I have enough information to answer the user.
Action: Finish["The capital of France is Paris, and its population is approximately 2.1 million residents."]
Pause
"""

class Agent:
    def __init__(self, system_prompt: str = REACT_SYSTEM_PROMPT):
        self.system = system_prompt
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.messages = [
            {"role": "system", "content": self.system}
        ]

    def _call_llm(self) -> str:
        """Call the OpenAI LLM and enforce stopping at 'Pause'"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.messages,
                temperature=0.1,  # Keep reasoning deterministic
                stop=["Observation:"] # Ensure the model stops before hallucinating observation (fallback alongside 'Pause')
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"LLM Error: {str(e)}"

    def execute(self, query: str):
        """The core ReAct Loop"""
        print(f"\n============================================\n[User Query]: {query}\n============================================")
        self.messages.append({"role": "user", "content": query})
        
        iteration = 0
        max_iterations = 5
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- [Iteration {iteration}] ---")
            
            # 1. Call LLM
            llm_response = self._call_llm()
            print(f"{llm_response}")
            
            # Record LLM output in history
            self.messages.append({"role": "assistant", "content": llm_response})
            
            # 2. Parse Action
            # We look for Action: Search["query"] or Action: Finish["answer"]
            action_match = re.search(r'Action: (.*?)\["(.*?)"\]', llm_response, re.DOTALL)
            
            if not action_match:
                # If the agent messes up formatting but provides an answer, try to salvage
                print(f"[Warning: Formatting error from LLM. No valid Action found.]")
                break
                
            tool_name = action_match.group(1).strip()
            tool_args = action_match.group(2).strip()
            
            if tool_name == "Finish":
                print(f"\n[Final Answer]: {tool_args}")
                return tool_args
                
            elif tool_name == "Search":
                # 3. Call Tool
                print(f"\n[Executing Search]: {tool_args} ...")
                observation = search(tool_args)
                obs_text = f"Observation: {observation}"
                
                print(f"[Search Results]:\n{observation[:300]}...\n")
                
                # 4. Update History
                self.messages.append({"role": "user", "content": obs_text})
            else:
                print(f"\n[Error: Invalid Tool Called]: {tool_name}")
                self.messages.append({"role": "user", "content": f"Observation: Invalid tool '{tool_name}'. Available tool is 'Search'."})
                
        if iteration >= max_iterations:
            print(f"\n[Warning]: Agent reached maximum iterations ({max_iterations}) and was forcibly stopped.")
            
        return "Failed to find answer within iteration limit."
