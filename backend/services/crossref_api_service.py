"""
Crossref API Service

Handles communication with Crossref API for DOI registration and management.

API Documentation: https://www.crossref.org/documentation/register-maintain-records/
Test Environment: https://test.crossref.org/
Production: https://doi.crossref.org/
"""

import httpx
from typing import Optional, Dict, List
from datetime import datetime
import asyncio
from enum import Enum


class CrossrefEnvironment(str, Enum):
    """Crossref API environments."""
    TEST = "test"
    PRODUCTION = "production"


class DOIDepositStatus(str, Enum):
    """DOI deposit status values."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    SUCCESS = "success"
    FAILED = "failed"
    WARNING = "warning"


class CrossrefAPIService:
    """Service for interacting with Crossref DOI registration API."""

    def __init__(
        self,
        username: str,
        password: str,
        environment: CrossrefEnvironment = CrossrefEnvironment.TEST,
        timeout: int = 30
    ):
        """
        Initialize Crossref API service.

        Args:
            username: Crossref depositor username
            password: Crossref depositor password
            environment: test or production
            timeout: Request timeout in seconds
        """
        self.username = username
        self.password = password
        self.environment = environment
        self.timeout = timeout

        # Set base URL based on environment
        if environment == CrossrefEnvironment.TEST:
            self.base_url = "https://test.crossref.org"
        else:
            self.base_url = "https://doi.crossref.org"

        self.deposit_url = f"{self.base_url}/servlet/deposit"
        self.query_url = f"{self.base_url}/servlet/query"

    async def deposit_doi(
        self,
        xml_content: str,
        filename: Optional[str] = None
    ) -> Dict:
        """
        Deposit DOI metadata to Crossref.

        Args:
            xml_content: Crossref XML content
            filename: Optional filename for the deposit

        Returns:
            Dictionary with deposit results including batch_id and status
        """
        if not filename:
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            filename = f"crossref_deposit_{timestamp}.xml"

        # Prepare multipart form data
        files = {
            'mdFile': (filename, xml_content.encode('utf-8'), 'application/xml')
        }

        data = {
            'operation': 'doMDUpload',
            'login_id': self.username,
            'login_passwd': self.password
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.deposit_url,
                    data=data,
                    files=files
                )

                response.raise_for_status()

                # Parse response
                return self._parse_deposit_response(response.text)

        except httpx.HTTPError as e:
            return {
                'success': False,
                'status': DOIDepositStatus.FAILED,
                'error': str(e),
                'message': f"HTTP error occurred: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'status': DOIDepositStatus.FAILED,
                'error': str(e),
                'message': f"Unexpected error: {str(e)}"
            }

    def _parse_deposit_response(self, response_text: str) -> Dict:
        """
        Parse Crossref deposit response.

        Response format:
        - Success: "SUCCESS\n[batch_id]\n[submission_id]\n[record_count]"
        - Failure: "FAILURE\n[error_message]"
        """
        lines = response_text.strip().split('\n')

        if not lines:
            return {
                'success': False,
                'status': DOIDepositStatus.FAILED,
                'error': 'Empty response from Crossref',
                'message': 'No response received'
            }

        status = lines[0].upper()

        if status == 'SUCCESS':
            result = {
                'success': True,
                'status': DOIDepositStatus.SUBMITTED,
                'message': 'DOI deposit submitted successfully'
            }

            # Extract batch ID and other info
            if len(lines) > 1:
                result['batch_id'] = lines[1]
            if len(lines) > 2:
                result['submission_id'] = lines[2]
            if len(lines) > 3:
                result['record_count'] = int(lines[3]) if lines[3].isdigit() else 0

            return result

        else:
            # Parse error message
            error_message = '\n'.join(lines[1:]) if len(lines) > 1 else 'Unknown error'

            return {
                'success': False,
                'status': DOIDepositStatus.FAILED,
                'error': error_message,
                'message': f"Deposit failed: {error_message}"
            }

    async def query_doi_status(self, doi: str) -> Dict:
        """
        Query the status of a DOI registration.

        Args:
            doi: The DOI to query (without https://doi.org/ prefix)

        Returns:
            Dictionary with DOI status information
        """
        params = {
            'usr': self.username,
            'pwd': self.password,
            'doi': doi,
            'format': 'json'
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.query_url,
                    params=params
                )

                response.raise_for_status()

                # Parse JSON response
                data = response.json()

                return {
                    'success': True,
                    'doi': doi,
                    'status': self._map_crossref_status(data.get('status')),
                    'registered': data.get('registered', False),
                    'data': data
                }

        except httpx.HTTPError as e:
            return {
                'success': False,
                'doi': doi,
                'error': str(e),
                'message': f"Failed to query DOI status: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'doi': doi,
                'error': str(e),
                'message': f"Unexpected error: {str(e)}"
            }

    async def query_batch_status(self, batch_id: str) -> Dict:
        """
        Query the status of a batch deposit.

        Args:
            batch_id: The batch ID from deposit response

        Returns:
            Dictionary with batch status information
        """
        params = {
            'usr': self.username,
            'pwd': self.password,
            'doi_batch_id': batch_id,
            'format': 'json'
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.query_url,
                    params=params
                )

                response.raise_for_status()

                # Parse JSON response
                data = response.json()

                return {
                    'success': True,
                    'batch_id': batch_id,
                    'status': self._map_crossref_status(data.get('status')),
                    'records_total': data.get('records_total', 0),
                    'records_success': data.get('records_success', 0),
                    'records_failed': data.get('records_failed', 0),
                    'records_warning': data.get('records_warning', 0),
                    'data': data
                }

        except httpx.HTTPError as e:
            return {
                'success': False,
                'batch_id': batch_id,
                'error': str(e),
                'message': f"Failed to query batch status: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'batch_id': batch_id,
                'error': str(e),
                'message': f"Unexpected error: {str(e)}"
            }

    def _map_crossref_status(self, crossref_status: Optional[str]) -> DOIDepositStatus:
        """Map Crossref API status to internal status enum."""
        if not crossref_status:
            return DOIDepositStatus.PENDING

        status_lower = crossref_status.lower()

        if status_lower in ['success', 'completed']:
            return DOIDepositStatus.SUCCESS
        elif status_lower in ['failed', 'error']:
            return DOIDepositStatus.FAILED
        elif status_lower == 'warning':
            return DOIDepositStatus.WARNING
        elif status_lower in ['submitted', 'pending', 'in_progress']:
            return DOIDepositStatus.SUBMITTED
        else:
            return DOIDepositStatus.PENDING

    async def update_doi_metadata(
        self,
        xml_content: str,
        filename: Optional[str] = None
    ) -> Dict:
        """
        Update existing DOI metadata.

        This is the same as deposit_doi - Crossref handles updates automatically
        when you submit metadata for an existing DOI.

        Args:
            xml_content: Updated Crossref XML content
            filename: Optional filename for the deposit

        Returns:
            Dictionary with update results
        """
        return await self.deposit_doi(xml_content, filename)

    async def deposit_correction(
        self,
        original_doi: str,
        correction_xml: str,
        filename: Optional[str] = None
    ) -> Dict:
        """
        Deposit a correction for an existing DOI.

        Args:
            original_doi: The DOI being corrected
            correction_xml: Crossref XML with correction metadata
            filename: Optional filename

        Returns:
            Dictionary with correction deposit results
        """
        if not filename:
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            safe_doi = original_doi.replace('/', '_')
            filename = f"crossref_correction_{safe_doi}_{timestamp}.xml"

        return await self.deposit_doi(correction_xml, filename)

    def validate_doi_format(self, doi: str) -> bool:
        """
        Validate DOI format.

        Args:
            doi: DOI string to validate

        Returns:
            True if valid format, False otherwise
        """
        # DOI format: 10.xxxx/suffix
        import re
        pattern = r'^10\.\d{4,}/[^\s]+$'
        return bool(re.match(pattern, doi))

    async def test_connection(self) -> Dict:
        """
        Test connection to Crossref API.

        Returns:
            Dictionary with connection test results
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/servlet/ping",
                    auth=(self.username, self.password)
                )

                return {
                    'success': response.status_code == 200,
                    'status_code': response.status_code,
                    'environment': self.environment.value,
                    'message': 'Connection successful' if response.status_code == 200 else 'Connection failed'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'environment': self.environment.value,
                'message': f"Connection test failed: {str(e)}"
            }


# Convenience functions

async def deposit_manuscript_doi(
    manuscript: dict,
    depositor_info: dict,
    journal_metadata: dict,
    crossref_credentials: dict,
    environment: CrossrefEnvironment = CrossrefEnvironment.TEST
) -> Dict:
    """
    Convenience function to deposit a single manuscript DOI.

    Args:
        manuscript: Manuscript data
        depositor_info: Depositor information
        journal_metadata: Journal metadata
        crossref_credentials: Dict with 'username' and 'password'
        environment: test or production

    Returns:
        Deposit result dictionary
    """
    from services.crossref_xml_service import generate_crossref_xml_for_manuscript

    # Generate Crossref XML
    xml_content = generate_crossref_xml_for_manuscript(
        manuscript=manuscript,
        depositor_info=depositor_info,
        journal_metadata=journal_metadata
    )

    # Initialize API service
    api_service = CrossrefAPIService(
        username=crossref_credentials['username'],
        password=crossref_credentials['password'],
        environment=environment
    )

    # Deposit to Crossref
    result = await api_service.deposit_doi(xml_content)

    return result
