# Assignment 2: Reasoning & Action Taking Report

**Due Date:** 3/12 - 3/25
**TA Name:** 陳柏安
**Student ID:** 114522065
**Name:** 郭亭宜

---

## Section 1: Implementation Logic

### System Prompt Strategy
My System Prompt explicitly defines the ReAct loop structure and strict formatting rules to prevent output parsing failures. 

```text
You are a ReAct (Reasoning and Acting) Agent. You are designed to answer user queries by interlacing thoughts, actions (tool use), and observations.

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
... [Instructions ensuring specific Action formatting] ...

# Few-Shot Example:
User: "What is the capital of France and what is its population?"
Thought: I need to find the capital of France first, and then I will search for its population. I should search for "capital of France".
Action: Search["capital of France"]
Pause
Observation: Result 1: Paris is the capital and most populous city of France.
Thought: The capital is Paris. Now I need to find the population of Paris.
Action: Search["population of Paris 2024"]
Pause ...
```

**Why this Few-Shot example helps the model:**
Zero-shot prompting often leads to the LLM either answering directly without tools or ignoring edge cases. By providing a clear, complete 3-step cycle (`Thought -> Search -> Observation -> Thought -> Search -> Observation -> Finish`), the model leverages **In-Context Learning**. It perfectly mimicking the exact formatting (`Action: Search["..."]`) and logic sequence (breaking down the capital finding first, then the population). This drastically reduces formatting hallucinations and ensures logical persistence.

### The Loop Mechanism
My Python script feeds the "Observation" back into the LLM's context window through a `while` loop (capped at 5 iterations). 
1. The LLM gets the entire `self.messages` history, and predicts `Thought` & `Action`.
2. I append the LLM's response to `self.messages` as an `assistant` role.
3. I parse the `Action: Search["query"]` regex, run the Tavily `search()` Python function, and format the output as `Observation: [...]`.
4. I append this new observation back into `self.messages` as a `user` role.
5. Crucially, the OpenAI API configuration uses `stop=["Observation:"]`. This explicitly forces the LLM to halt generation right after emitting the `Pause` token, guaranteeing the environment (my Python script) executes the tool rather than the LLM hallucinating fake tool results.

---

## Section 2: Benchmark Traces (The Evidence)

### Task 1: Planning & Quantitative Reasoning
**Query:** "What fraction of Japan's population is Taiwan's population as of 2025?"

**Console Trace:**
```text
============================================
[User Query]: What fraction of Japan's population is Taiwan's population as of 2025?
============================================

--- [Iteration 1] ---
Thought: I need to find the population of Japan as of 2025 and the population of Taiwan as of the same year. I will start by searching for the population of Japan in 2025. 
Action: Search["Japan population 2025"] 

[Search Results]:
Result 1:
Title: Japan Population (1950-2025) - Macrotrends...

--- [Iteration 2] ---
Thought: I have found that the population of Japan in 2025 is estimated to be around 121,960,408. Now, I need to find the population of Taiwan in 2025 to calculate the fraction of Japan's population that Taiwan's population represents. I will search for the population of Taiwan in 2025. 
Action: Search["Taiwan population 2025"] 

[Search Results]:
Result 1:
Title: Taiwan Population (1950-2025) - Macrotrends...

--- [Iteration 3] ---
Thought: I have found that the population of Taiwan in 2025 is estimated to be approximately 23,974,031. Now I can calculate the fraction of Japan's population that Taiwan's population represents. Japan's population is 121,960,408 and Taiwan's population is 23,974,031. I will perform the calculation to find the fraction. 
Action: Finish["The fraction of Japan's population that is Taiwan's population as of 2025 is approximately 0.197, or 19.7%."] 
```
**Analysis:** 
The trace provides clear evidence of **Task Decomposition**. The agent did not attempt to search for the final ratio directly or guess the answer. Instead, it systematically recognized the need for two variables: it first executed `Search["Japan population 2025"]` in Iteration 1, stored the 121.9M result in its context, and then executed a separate `Search["Taiwan population 2025"]` in Iteration 2. Finally, in Iteration 3, it performed the mathematical calculation using the exact extracted figures.

### Task 2: Technical Specificity
**Query:** "Compare the main display specs of iPhone 15 and Samsung S24."

**Console Trace:**
```text
============================================
[User Query]: Compare the main display specs of iPhone 15 and Samsung S24.
============================================

--- [Iteration 1] ---
Thought: I need to gather the main display specifications for both the iPhone 15 and the Samsung S24. I will start by searching for the display specifications of the iPhone 15. 
Action: Search["iPhone 15 display specifications"] 

[Search Results]:
Result 1:
Title: Apple iPhone 15 - Specifications | One New Zealand
Content: # Apple iPhone 15. | Dimensions | 147.6 x 71.6 x 7.8 mm |. ### Screen and keys. | Screen type | XDR OLED touch screen, HDR10, Dolby Vision, 16 million colours |...

--- [Iteration 2] ---
Thought: I have gathered the display specifications for the iPhone 15. It features a 6.1-inch XDR OLED touch screen with HDR10 and Dolby Vision support. Now, I need to find the display specifications for the Samsung S24 to make a comparison. 
Action: Search["Samsung S24 display specifications"] 

[Search Results]:
Result 1:
Title: Samsung Galaxy S24 - Device Specifications
Content: Storage: 128 GB, 256 GB, 512 GB ; Display: 6.2 in, Dynamic AMOLED 2X, 1080 x 2340 pixels, 24 bit...

--- [Iteration 3] ---
Thought: I have obtained the display specifications for the Samsung S24. It features a 6.2-inch Dynamic AMOLED 2X display with a resolution of 1080 x 2340 pixels... I now have enough information to form the final answer. 
Action: Finish["The iPhone 15 features a 6.1-inch XDR OLED display with a resolution of 1179 x 2556 pixels and supports HDR10 and Dolby Vision. The Samsung S24 has a 6.2-inch Dynamic AMOLED 2X display with a resolution of 1080 x 2340 pixels, supports HDR10+, and has a peak brightness of 2600 nits."] 
```
**Analysis:** 
The evidence shows strong **Data Retrieval** specificity. The agent successfully retrieved the exact display panel types evaluating the technical nuances: correctly identifying not just the sizes (6.1-inch vs 6.2-inch) but retrieving the precise technical terminology (XDR OLED for Apple, Dynamic AMOLED 2X for Samsung), as well as extracting hardware specific specifications like Dolby Vision vs HDR10+. 

### Task 3: Resilience & Reflection Test
**Query:** "Who is the CEO of the startup 'Morphic' AI search?"

**Console Trace:**
```text
============================================
[User Query]: Who is the CEO of the startup 'Morphic' AI search?
============================================

--- [Iteration 1] ---
Thought: I need to find out who the CEO of the startup 'Morphic' is. I will search for "Morphic AI search CEO". 
Action: Search["Morphic AI search CEO"] 

[Search Results]:
Result 1:
Title: Jaynti Kanani - Founder & Chief Executive Officer at Morphic
Content: Jaynti Kanani is the Founder and Chief Executive Officer at Morphic, blending technology and creative production. Their background reflects a strong focus

Result 2:
Title: Morphic holding CEO sells shares worth o...

--- [Iteration 2] ---
Thought: The first result indicates that Jaynti Kanani is the CEO of Morphic, while the second result refers to a different company (Morphic Holdings) with a different CEO, Praveen P. Tipirneni. Since the user is asking about 'Morphic' AI search, I will focus on the information about Jaynti Kanani. I now have enough information to answer the user's question. 
Action: Finish["The CEO of Morphic AI search is Jaynti Kanani."] 
```
**Analysis:** 
The trace exhibits strong **Agentic Reflection**. When searching for "Morphic", the search engine returned ambiguous results (a mix of Morphic AI and another physical company, Morphic Holding). Instead of immediately stopping or conflating the results, the agent engaged its reasoning capability to verify the context. It explicitly reflected (Self-Correction/Disambiguation) that "Result 2 refers to a different company," actively isolating the correct entity (Jaynti Kanani) relative to the original user query parameters.
