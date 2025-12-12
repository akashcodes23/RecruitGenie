from crewai import Agent, Task, Crew

class JobDescriptionOptimizer:
    def __init__(self):
        self.agent = Agent(
            role="Job Description Optimizer",
            goal="Optimize job postings to attract excellent applicants.",
            backstory="You are a leading HR AI with expertise in writing inclusive job postings.",
            verbose=True
        )

    def optimize(self, raw_description: str) -> str:
        task = Task(
            description=f"Rewrite and optimize this job description: {raw_description}",
            expected_output="Return a less biased, clearer job description optimized for qualified talent.",
            agent=self.agent
        )
        crew = Crew(agents=[self.agent], tasks=[task])
        result = crew.kickoff()
        return result

