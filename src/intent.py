from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class UserIntent:
    # --------------------------------------------------
    # Intent we CAN use directly in this V1
    # --------------------------------------------------

    exploration_preference: Optional[str] = None
    # familiar / balanced / exploratory

    popularity_preference: Optional[str] = None
    # popular / neutral / niche

    # --------------------------------------------------
    # Constraints the user may ask for
    # but we may NOT be able to verify from Retailrocket
    # --------------------------------------------------

    requested_brand: Optional[str] = None

    max_price: Optional[float] = None

    min_price: Optional[float] = None

    use_case: Optional[str] = None

    priority_features: Optional[List[str]] = None

    avoid_features: Optional[List[str]] = None

    # --------------------------------------------------
    # Explicit grounding / honesty fields
    # --------------------------------------------------

    supported_preferences: Optional[List[str]] = None

    unverifiable_constraints: Optional[List[str]] = None

    def to_dict(self):
        return asdict(self)