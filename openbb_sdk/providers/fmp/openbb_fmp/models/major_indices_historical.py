"""FMP Major Indices end of day fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.major_indices_historical import (
    MajorIndicesHistoricalData,
    MajorIndicesHistoricalQueryParams,
)
from openbb_provider.utils.helpers import get_querystring
from pydantic import Field, NonNegativeInt, validator

from openbb_fmp.utils.helpers import get_data_many


class FMPMajorIndicesHistoricalQueryParams(MajorIndicesHistoricalQueryParams):
    """FMP Major Indices end of day Query.

    Source: https://site.financialmodelingprep.com/developer/docs/historical-index-price-api/
    """

    timeseries: Optional[NonNegativeInt] = Field(
        default=None, description="Number of days to look back."
    )
    interval: Literal[
        "1min", "5min", "15min", "30min", "1hour", "4hour", "1day"
    ] = Field(default="1day", description="Data granularity.")


class FMPMajorIndicesHistoricalData(MajorIndicesHistoricalData):
    """FMP Major Indices end of day Data."""

    adj_close: Optional[float] = Field(
        description="Adjusted Close Price of the symbol.",
        default=None,
    )
    unadjusted_volume: Optional[float] = Field(
        description="Unadjusted volume of the symbol.",
        default=None,
    )
    change: Optional[float] = Field(
        description="Change in the price of the symbol from the previous day.",
        default=None,
    )
    change_percent: Optional[float] = Field(
        description=r"Change \% in the price of the symbol.",
        default=None,
    )
    label: Optional[str] = Field(
        description="Human readable format of the date.", default=None
    )
    change_over_time: Optional[float] = Field(
        description=r"Change \% in the price of the symbol over a period of time.",
        default=None,
    )

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v) -> datetime:  # pylint: disable=E0213
        """Return the date as a datetime object."""
        try:
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return datetime.strptime(v, "%Y-%m-%d")


class FMPMajorIndicesHistoricalFetcher(
    Fetcher[
        FMPMajorIndicesHistoricalQueryParams,
        List[FMPMajorIndicesHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPMajorIndicesHistoricalQueryParams:
        """Transform the query params."""
        return FMPMajorIndicesHistoricalQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPMajorIndicesHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        query_str = (
            get_querystring(query.dict(), ["symbol"])
            .replace("start_date", "from")
            .replace("end_date", "to")
        )

        url_params = f"{query.symbol}?{query_str}&apikey={api_key}"
        url = f"{base_url}/historical-chart/{query.interval}/%5E{url_params}"

        if query.interval == "1day":
            url = f"{base_url}/historical-price-full/index/%5E{url_params}"

        return get_data_many(url, "historical", **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPMajorIndicesHistoricalData]:
        """Return the transformed data."""
        return [FMPMajorIndicesHistoricalData(**d) for d in data]