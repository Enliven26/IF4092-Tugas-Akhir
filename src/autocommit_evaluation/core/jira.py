from abc import ABC, abstractmethod

from jira import JIRA, Issue


class IJira(ABC):
    @abstractmethod
    def get_ticket_content(
        self,
        server_url: str,
        ticket_id: str,
    ) -> str:
        pass


class Jira(IJira):
    def __get_formatted_issue(self, issue: Issue) -> str:
        summary = issue.fields.summary
        description = issue.fields.description or "No description provided."
        issue_type = str(issue.fields.issuetype)
        priority = (
            str(issue.fields.priority) if issue.fields.priority else "No priority set"
        )

        return (
            f"Ticket ID: {issue.key}\n"
            f"Issue Summary: {summary}\n"
            f"Issue Type: {issue_type}\n"
            f"Priority: {priority}\n\n"
            f"Description:\n{description}"
        )

    def get_ticket_content(
        self,
        server_url: str,
        ticket_id: str,
    ) -> str:
        jira = JIRA(server_url)
        issue = jira.issue(ticket_id)
        return self.__get_formatted_issue(issue)
