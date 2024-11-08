from typing import List, Optional
from pydantic import BaseModel, Field

class Organisation(BaseModel):
    """Information about an organisation."""
    org_name: Optional[str] = Field(
        default=None, description="The full name of the organisation, not an abbreviation"
    )
    org_url: Optional[str] = Field(
        default=None, description="The URL of the organisation"
    )
    org_abbrev: Optional[str] = Field(
        default=None, description="The abbreviation of the organisation name, typically in capital letters or parentheses"
    )

class Data(BaseModel):
    """Extracted data about organisations."""

    organisations: List[Organisation]
