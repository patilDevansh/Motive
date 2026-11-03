from abc import ABC, abstractmethod

from src.intent import UserIntent


class LLMProvider(ABC):

    @abstractmethod
    def parse_intent(
        self,
        user_text: str
    ) -> UserIntent:
        """
        Convert natural-language user preferences
        into our structured UserIntent schema.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_explanation(
        self,
        recommendation_evidence,
        intent: UserIntent | None = None
    ):
        """
        Convert grounded recommendation evidence
        into readable explanations.

        The implementation must not introduce
        unsupported product claims.
        """
        raise NotImplementedError