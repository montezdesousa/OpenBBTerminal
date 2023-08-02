"""FMP Share Statistics Fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.share_statistics import (
    ShareStatisticsData,
    ShareStatisticsQueryParams,
)
from pydantic import validator

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPShareStatisticsQueryParams(ShareStatisticsQueryParams):
    """FMP Income Statement QueryParams.

    Source: https://site.financialmodelingprep.com/developer/docs/shares-float-api/
    """


class FMPShareStatisticsData(ShareStatisticsData):
    """FMP Share Statistics Data."""

    class Config:
        fields = {
            "free_float": "freeFloat",
            "float_shares": "floatShares",
            "outstanding_shares": "outstandingShares",
        }

    @validator("date", pre=True)
    def date_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")


class FMPShareStatisticsFetcher(
    Fetcher[
        ShareStatisticsQueryParams,
        ShareStatisticsData,
        FMPShareStatisticsQueryParams,
        FMPShareStatisticsData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPShareStatisticsQueryParams:
        return FMPShareStatisticsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPShareStatisticsQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPShareStatisticsData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "shares_float", api_key, query)

        return get_data_many(url, FMPShareStatisticsData)

    @staticmethod
    def transform_data(
        data: List[FMPShareStatisticsData],
    ) -> List[FMPShareStatisticsData]:
        return data