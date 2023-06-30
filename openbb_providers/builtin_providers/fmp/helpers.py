"""FMP Helpers Module."""

# IMPORT STANDARD
from datetime import datetime
from typing import List, Optional, Type, TypeVar, Union

# IMPORT THIRD-PARTY
import requests
from pydantic import BaseModel, NonNegativeInt, PositiveFloat, validator
from requests.exceptions import SSLError

from openbb_provider.model.abstract.data import Data

# IMPORT INTERNAL
from openbb_provider.provider.abstract.fetcher import QueryParamsType
from openbb_provider.provider.provider_helpers import (
    BasicResponse,
    get_querystring,
    request,
)

T = TypeVar("T", bound=BaseModel)


def get_data(url: str) -> Union[list, dict]:
    try:
        r: Union[requests.Response, BasicResponse] = requests.get(url, timeout=10)
    except SSLError:
        r = request(url)
    if r.status_code == 404:
        raise RuntimeError("FMP endpoint doesn't exist")

    data = r.json()
    if r.status_code != 200:
        message = data.get("message", "unknown error")
        raise RuntimeError(f"Error in FMP request: {message}")

    if "Error Message" in data:
        raise RuntimeError("FMP Error Message: " + data["Error Message"])

    if len(data) == 0:
        raise RuntimeError("No results found. Try adjusting the query parameters.")

    return data


def create_url(
    version: int,
    endpoint: str,
    api_key: str,
    query: Optional[QueryParamsType] = None,
    exclude: Optional[List[str]] = None,
) -> str:
    """Creates a URL for the FMP API.

    Parameters:
    -----------
    version: int
        The version of the API to use.
    endpoint: str
        The endpoint to use.
    api_key: str
        The API key to use.
    query: Optional[QueryParamsType]
        The dictionary to be turned into a querystring.
    exclude: List[str]
        The keys to be excluded from the querystring.

    Returns:
    --------
    str
        The querystring.

    """
    the_dict = {} if not query else query.dict()
    query_string = get_querystring(the_dict, exclude or [])
    base_url = f"https://financialmodelingprep.com/api/v{version}/"
    return f"{base_url}{endpoint}?{query_string}&apikey={api_key}"


def get_data_many(
    url: str, to_schema: Type[T], sub_dict: Optional[str] = None
) -> List[T]:
    """Get data from FMP endpoint and convert to list of schemas.

    Parameters:
    -----------
    url: str
        The URL to get the data from.
    to_schema: T
        The schema to convert the data to.
    sub_dict: Optional[str]
        The sub-dictionary to use.
    """
    data = get_data(url)
    if sub_dict and isinstance(data, dict):
        data = data.get(sub_dict, [])
    if isinstance(data, dict):
        raise ValueError("Expected list of dicts, got dict")
    return [to_schema(**d) for d in data]


def get_data_one(url: str, to_schema: Type[T]) -> T:
    """Get data from FMP endpoint and convert to schema."""
    data = get_data(url)
    if isinstance(data, list):
        raise ValueError("Expected dict with lists, got list")
    return to_schema(**data)


class BaseStockPriceData(Data):
    open: PositiveFloat
    high: PositiveFloat
    low: PositiveFloat
    close: PositiveFloat
    volume: NonNegativeInt
    date: datetime

    @validator("date", pre=True)
    def time_validate(cls, v: str) -> datetime:  # pylint: disable=E0213
        if len(v) < 12:
            return datetime.strptime(v, "%Y-%m-%d")
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")