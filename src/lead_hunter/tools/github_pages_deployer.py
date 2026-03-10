import os
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class GithubPagesInput(BaseModel):
    filename: str = Field(description="HTML filename to deploy (e.g. 'thai_bistro.html')")
    html_content: str = Field(description="Full HTML content of the demo page")


class GithubPagesDeployerTool(BaseTool):
    name: str = "GitHub Pages Deployer"
    description: str = (
        "Deploys an HTML file to the gh-pages branch of the project repo and returns "
        "the live GitHub Pages URL. Input: filename, html_content. "
        "Returns the public URL or an error message."
    )
    args_schema: Type[BaseModel] = GithubPagesInput

    def _run(self, filename: str, html_content: str) -> str:
        token = os.getenv("GITHUB_TOKEN")
        repo_name = os.getenv("GITHUB_REPO", "Ariec18/bring-me-leeds-crew")

        if not token:
            return "ERROR: GITHUB_TOKEN not set in environment."

        try:
            from github import Github, GithubException
        except ImportError:
            return "ERROR: PyGithub not installed — run `uv add PyGithub`."

        g = Github(token)

        try:
            repo = g.get_repo(repo_name)
        except Exception as e:
            return f"ERROR: Could not access repo '{repo_name}' — {str(e)}"

        # Ensure gh-pages branch exists
        try:
            repo.get_branch("gh-pages")
        except Exception:
            # Create gh-pages from default branch
            try:
                default_sha = repo.get_branch(repo.default_branch).commit.sha
                repo.create_git_ref(ref="refs/heads/gh-pages", sha=default_sha)
            except Exception as e:
                return f"ERROR: Could not create gh-pages branch — {str(e)}"

        path = f"demos/{filename}"
        commit_msg = f"Deploy demo: {filename}"

        try:
            existing = repo.get_contents(path, ref="gh-pages")
            repo.update_file(
                path=path,
                message=commit_msg,
                content=html_content,
                sha=existing.sha,
                branch="gh-pages",
            )
        except Exception:
            try:
                repo.create_file(
                    path=path,
                    message=commit_msg,
                    content=html_content,
                    branch="gh-pages",
                )
            except Exception as e:
                return f"ERROR: Could not push file to gh-pages — {str(e)}"

        owner, repo_slug = repo_name.split("/")
        url = f"https://{owner}.github.io/{repo_slug}/demos/{filename}"
        return f"SUCCESS: {url}"
