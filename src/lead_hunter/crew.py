from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, FileWriterTool, FileReadTool

from lead_hunter.tools.google_maps_tool import GoogleMapsSearchTool
from lead_hunter.tools.website_generator import WebsiteGeneratorTool
from lead_hunter.tools.github_pages_deployer import GithubPagesDeployerTool
from lead_hunter.tools.email_sender import EmailSenderTool


@CrewBase
class LeadHunterCrew:
    """Lead generation crew — Google Maps → demo site → proposal → outreach."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # ── AGENTS ──────────────────────────────────────────────────────────────

    @agent
    def lead_scout(self) -> Agent:
        return Agent(
            config=self.agents_config["lead_scout"],
            tools=[GoogleMapsSearchTool(), SerperDevTool()],
        )

    @agent
    def business_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["business_analyst"],
            tools=[ScrapeWebsiteTool(), SerperDevTool()],
        )

    @agent
    def website_creator(self) -> Agent:
        return Agent(
            config=self.agents_config["website_creator"],
            tools=[WebsiteGeneratorTool(), GithubPagesDeployerTool(), FileWriterTool()],
        )

    @agent
    def proposal_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["proposal_writer"],
            tools=[FileWriterTool(), FileReadTool()],
        )

    @agent
    def outreach_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["outreach_manager"],
            tools=[EmailSenderTool()],
        )

    # ── TASKS ───────────────────────────────────────────────────────────────

    @task
    def find_leads_task(self) -> Task:
        return Task(config=self.tasks_config["find_leads_task"])

    @task
    def analyze_business_task(self) -> Task:
        return Task(config=self.tasks_config["analyze_business_task"])

    @task
    def create_demo_website_task(self) -> Task:
        return Task(config=self.tasks_config["create_demo_website_task"])

    @task
    def write_proposal_task(self) -> Task:
        return Task(config=self.tasks_config["write_proposal_task"])

    @task
    def send_outreach_task(self) -> Task:
        return Task(
            config=self.tasks_config["send_outreach_task"],
            # human_input=True pauses the pipeline here so you can review
            # all emails before they go out. Type 'yes' to proceed, or
            # modify the agent's plan in natural language.
            human_input=True,
            output_file="output/outreach_report.md",
        )

    # ── CREW ────────────────────────────────────────────────────────────────

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
