# Verbose

**1. The Research Question** "In this project, we conducted a **pilot study** to investigate how a **proactive, context-aware agent** influences user frustration and task engagement. Specifically, we explored whether a **virtual agent** can help users actively manage negative emotions during a high-difficulty task, rather than just preventing them."

**2. The Design & Evaluation Approach** "To test this, we developed a **low-fidelity prototype** called 'Flappy Coach.' The system integrates an LLM for intelligence and a Text-to-Speech engine for empathetic vocal delivery.

We employed a **mixed-methods evaluation** in a **controlled setting(student housing)** with 5 participants.

- **The Task:** Users played a modified version of 'Flappy Bird,' selected for its steep difficulty.
    
- **The Measures:** We collected **subjective measures** via Likert-scale surveys and open-ended feedback to assess agent perception and frustration."
    

**3. The Results & Conclusion** "Our **preliminary findings** from this pilot study reveal a distinct contrast between task difficulty and emotional support:

- **Task Perception:** While the game was successfully validated as challenging (Mean=5.6), the self-reported frustration was lower than anticipated (Mean=3.6).
    
- **Agent Perception (UX Goals):** In terms of **User Experience**, the prototype succeeded as a support figure. Participants rated the agent as highly supportive (Mean=5.6) and the voice as calming (Mean=6.2).
    
- **Impact:** Most importantly, **task persistence** improved. 4 out of 5 participants reported that the agent's active encouragement directly motivated them to keep trying.
    
- **Design Iteration:** However, we identified a need for better **active listening** capabilities, as users felt the agent did not fully 'hear' them (Mean=3.6).
    

**Conclusion:** This pilot confirms the **feasibility** of our design. While the current **interaction fidelity** needs improvement to reduce repetition , the results indicate that proactive affective agents can successfully foster motivation and persistence in stressful environments."

# Bullet Points

**1. The Research Question**

- **Context:** Traditional HCI focuses on _preventing_ negative emotions, often overlooking how to help users _manage_ them once they arise .
    
- **Core Question:** Can a proactive, context-aware virtual agent alleviate user frustration and improve task engagement during a challenging activity?
    
- **Theoretical Basis:** Based on the "Computers Are Social Actors" (CASA) paradigm—users apply social norms to machines .
    

**2. The Design & Evaluation Approach**

- **Prototype ("Flappy Coach"):**
    
    - **System:** Very minimally embodied agent using an LLM (Gemini API) for intelligence and Text-to-Speech (ElevenLabs) for empathetic vocal delivery .
        
    - **Capabilities:** Monitors game events (crashes, score) and user vocal cues to provide real-time, context-sensitive support .
        
- **Methodology (Pilot Study):**
    
    - **Participants:** 5 university students in a controlled student housing setting .
        
    - **Task:** Playing a modified "Flappy Bird" game, chosen for its difficulty and potential to induce frustration .
        
    - **Measures:** Mixed-methods approach using Likert-scale surveys (subjective perception) and interaction recordings (task persistence) .
        

**3. The Results & Conclusion**

- **Task Difficulty vs. Frustration:**
    
    - **Difficulty:** Validated as high; every participant found the game challenging (Median: 6/7) .
        
    - **Frustration:** Lower than expected; only 2/5 participants reported high frustration (Mean: 3.6/7) .
        
- **Agent Perception (UX Goals):**
    
    - **Support:** Agent successfully perceived as supportive (Mean: 5.6/7) .
        
    - **Voice:** Universally rated as calming (Mean: 6.2/7) .
        
    - **Motivation:** 4/5 participants reported the agent's encouragement motivated them to keep trying; 1 user explicitly stated they wouldn't have persisted without it .
        
- **Areas for Improvement:**
    
    - **Active Listening:** Users felt the agent didn't fully "listen" (Mean: 3.6/7) .
        
    - **Repetition:** 40% found repeated phrases distracting .
        
- **Conclusion:** The pilot confirms feasibility. While interaction fidelity (listening/repetition) needs iteration, the _proactive_ support successfully fostered motivation and persistence, validating the potential of affective agents in high-stress tasks .