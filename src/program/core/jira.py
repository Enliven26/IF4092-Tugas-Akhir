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
        return f"{issue.fields.summary}\n\n{issue.fields.description or ''}"

    def get_ticket_content(
        self,
        server_url: str,
        ticket_id: str,
    ) -> str:
        jira = JIRA(server_url)
        issue = jira.issue(ticket_id)
        return self.__get_formatted_issue(issue)
