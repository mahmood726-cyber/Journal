"""
DataCite DOI registration service.
Alternative DOI provider to Crossref.
"""
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
import httpx
import json

from ..db.models import Manuscript


class DataCiteEnvironment:
    """DataCite API environments."""
    TEST = "test"
    PRODUCTION = "production"


class DataCiteResponse(BaseModel):
    """Response from DataCite API."""
    doi: str
    url: str
    state: str  # draft, findable, registered
    created: datetime
    updated: datetime


class DataCiteService:
    """
    Service for DataCite DOI registration.

    DataCite is an alternative DOI registration agency to Crossref,
    commonly used for datasets, software, and research outputs.

    Features:
    - JSON-based API (simpler than Crossref XML)
    - Supports draft DOIs
    - Rich metadata support
    - Test environment available
    """

    def __init__(
        self,
        repository_id: str,
        password: str,
        environment: str = DataCiteEnvironment.TEST,
        timeout: int = 30
    ):
        """
        Initialize DataCite service.

        Args:
            repository_id: DataCite repository ID (e.g., REPO.INST)
            password: Repository password
            environment: "test" or "production"
            timeout: Request timeout in seconds
        """
        self.repository_id = repository_id
        self.password = password
        self.environment = environment
        self.timeout = timeout

        if environment == DataCiteEnvironment.TEST:
            self.base_url = "https://api.test.datacite.org"
        else:
            self.base_url = "https://api.datacite.org"

    async def register_doi(
        self,
        doi: str,
        manuscript: Manuscript,
        url: str,
        state: str = "findable"  # draft, registered, findable
    ) -> DataCiteResponse:
        """
        Register or update DOI with DataCite.

        Args:
            doi: DOI to register (must start with your prefix)
            manuscript: Manuscript object
            url: Landing page URL for the DOI
            state: DOI state (draft, registered, findable)

        Returns:
            DataCiteResponse with registration details
        """
        # Generate DataCite metadata
        metadata = self._generate_metadata(doi, manuscript, url)

        # Set state
        metadata['data']['attributes']['event'] = state

        # Make API request
        async with httpx.AsyncClient(
            auth=(self.repository_id, self.password),
            timeout=self.timeout
        ) as client:
            response = await client.post(
                f"{self.base_url}/dois",
                json=metadata,
                headers={"Content-Type": "application/vnd.api+json"}
            )

            if response.status_code == 201:
                result = response.json()
                data = result['data']['attributes']

                return DataCiteResponse(
                    doi=data['doi'],
                    url=data['url'],
                    state=data['state'],
                    created=datetime.fromisoformat(data['created'].replace('Z', '+00:00')),
                    updated=datetime.fromisoformat(data['updated'].replace('Z', '+00:00'))
                )
            else:
                raise Exception(f"DataCite registration failed: {response.status_code} - {response.text}")

    async def update_doi(
        self,
        doi: str,
        manuscript: Manuscript,
        url: str
    ) -> DataCiteResponse:
        """Update existing DOI metadata."""
        metadata = self._generate_metadata(doi, manuscript, url)

        async with httpx.AsyncClient(
            auth=(self.repository_id, self.password),
            timeout=self.timeout
        ) as client:
            response = await client.put(
                f"{self.base_url}/dois/{doi}",
                json=metadata,
                headers={"Content-Type": "application/vnd.api+json"}
            )

            if response.status_code == 200:
                result = response.json()
                data = result['data']['attributes']

                return DataCiteResponse(
                    doi=data['doi'],
                    url=data['url'],
                    state=data['state'],
                    created=datetime.fromisoformat(data['created'].replace('Z', '+00:00')),
                    updated=datetime.fromisoformat(data['updated'].replace('Z', '+00:00'))
                )
            else:
                raise Exception(f"DataCite update failed: {response.status_code} - {response.text}")

    async def get_doi(self, doi: str) -> Dict:
        """Get DOI metadata from DataCite."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/dois/{doi}",
                headers={"Accept": "application/vnd.api+json"}
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"DOI not found: {response.status_code}")

    async def delete_doi(self, doi: str) -> bool:
        """
        Delete a draft DOI.
        Note: Only draft DOIs can be deleted, not registered/findable ones.
        """
        async with httpx.AsyncClient(
            auth=(self.repository_id, self.password),
            timeout=self.timeout
        ) as client:
            response = await client.delete(f"{self.base_url}/dois/{doi}")

            return response.status_code == 204

    def _generate_metadata(
        self,
        doi: str,
        manuscript: Manuscript,
        url: str
    ) -> Dict:
        """
        Generate DataCite JSON metadata.

        Follows DataCite Metadata Schema 4.4
        https://schema.datacite.org/meta/kernel-4.4/
        """
        # Build creators (authors)
        creators = []
        for author in manuscript.authors:
            creator = {
                "name": f"{author.full_name}",
                "nameType": "Personal",
                "givenName": author.full_name.split()[0] if ' ' in author.full_name else author.full_name,
                "familyName": author.full_name.split()[-1] if ' ' in author.full_name else author.full_name
            }

            # Add ORCID if available
            if author.orcid:
                creator["nameIdentifiers"] = [{
                    "nameIdentifier": f"https://orcid.org/{author.orcid}",
                    "nameIdentifierScheme": "ORCID",
                    "schemeUri": "https://orcid.org"
                }]

            # Add affiliation if available
            if author.affiliation:
                creator["affiliation"] = [{
                    "name": author.affiliation
                }]

            creators.append(creator)

        # Build titles
        titles = [{"title": manuscript.title}]

        # Build subjects (keywords)
        subjects = []
        if manuscript.keywords:
            subjects = [{"subject": kw} for kw in manuscript.keywords]

        # Build descriptions
        descriptions = []
        if manuscript.abstract:
            descriptions.append({
                "description": manuscript.abstract,
                "descriptionType": "Abstract"
            })

        # Build publication year
        publication_year = manuscript.published_at.year if manuscript.published_at else datetime.now().year

        # Build rights
        rights_list = [{
            "rights": "Creative Commons Attribution 4.0 International",
            "rightsUri": "https://creativecommons.org/licenses/by/4.0/",
            "rightsIdentifier": "CC-BY-4.0",
            "rightsIdentifierScheme": "SPDX",
            "schemeUri": "https://spdx.org/licenses/"
        }]

        # Build related identifiers (if manuscript has other IDs)
        related_identifiers = []
        if manuscript.pubmed_id:
            related_identifiers.append({
                "relatedIdentifier": manuscript.pubmed_id,
                "relatedIdentifierType": "PMID",
                "relationType": "IsIdenticalTo"
            })

        if manuscript.pmc_id:
            related_identifiers.append({
                "relatedIdentifier": manuscript.pmc_id,
                "relatedIdentifierType": "PMCID",
                "relationType": "IsIdenticalTo"
            })

        # Build dates
        dates = []
        if manuscript.published_at:
            dates.append({
                "date": manuscript.published_at.strftime("%Y-%m-%d"),
                "dateType": "Issued"
            })
        if manuscript.submitted_at:
            dates.append({
                "date": manuscript.submitted_at.strftime("%Y-%m-%d"),
                "dateType": "Submitted"
            })

        # Build complete metadata
        metadata = {
            "data": {
                "type": "dois",
                "attributes": {
                    "doi": doi,
                    "url": url,
                    "creators": creators,
                    "titles": titles,
                    "publisher": "Diamond Open Access Journal",  # Use actual journal name
                    "publicationYear": publication_year,
                    "resourceType": "JournalArticle",
                    "types": {
                        "resourceTypeGeneral": "Text",
                        "resourceType": "JournalArticle"
                    },
                    "subjects": subjects,
                    "descriptions": descriptions,
                    "rightsList": rights_list,
                    "schemaVersion": "http://datacite.org/schema/kernel-4"
                }
            }
        }

        # Add optional fields if available
        if related_identifiers:
            metadata['data']['attributes']['relatedIdentifiers'] = related_identifiers

        if dates:
            metadata['data']['attributes']['dates'] = dates

        # Add container information (journal)
        if manuscript.issue:
            metadata['data']['attributes']['container'] = {
                "type": "Series",
                "title": "Diamond Open Access Journal",  # Use actual journal name
                "volume": str(manuscript.volume) if manuscript.volume else None,
                "issue": str(manuscript.issue) if manuscript.issue else None
            }

        return metadata


def get_datacite_service(
    repository_id: str,
    password: str,
    test_mode: bool = True
) -> DataCiteService:
    """
    Get DataCite service instance.

    Args:
        repository_id: DataCite repository ID
        password: Repository password
        test_mode: Use test environment if True

    Returns:
        DataCiteService instance
    """
    environment = DataCiteEnvironment.TEST if test_mode else DataCiteEnvironment.PRODUCTION

    return DataCiteService(
        repository_id=repository_id,
        password=password,
        environment=environment
    )
