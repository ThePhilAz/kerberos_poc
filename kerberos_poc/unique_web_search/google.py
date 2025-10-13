from pydantic import BaseModel, Field

from httpx import Response

from kerberos_poc.unique_web_search.client import async_client
from kerberos_poc.unique_web_search.settings import env_settings

# Pagingation size fixed to 10 because of the Google Search API limit
PAGINATION_SIZE = 10


class GoogleSearchParameters(BaseModel):
    q: str
    cx: str
    key: str
    start: int
    num: int = PAGINATION_SIZE


class WebSearchResult(BaseModel):
    url: str
    title: str
    snippet: str = Field(
        ...,
        description="A short description of the content found on this website",
    )
    content: str = Field(
        default="",
        description="The content of the website",
    )


class GoogleSearch:
    def __init__(self):
        self.api_key = env_settings.google_search_api_key
        self.search_engine_id = env_settings.google_search_engine_id
        self.api_endpoint = env_settings.google_search_api_endpoint

    async def search(
        self, query, fetch_size: int = PAGINATION_SIZE, debug: bool = False
    ) -> list[WebSearchResult]:
        responses = []

        for start_index in range(1, fetch_size + 1, PAGINATION_SIZE):
            effective_num_fetch = min(fetch_size - start_index + 1, PAGINATION_SIZE)

            assert self.search_engine_id is not None
            assert self.api_key is not None
            assert self.api_endpoint is not None

            query_params = GoogleSearchParameters(
                q=query,
                cx=self.search_engine_id,
                key=self.api_key,
                start=start_index,
                num=effective_num_fetch,
            ).model_dump(exclude_none=True)

            params = {
                "url": self.api_endpoint,
                "params": query_params,
            }

            async with async_client() as client:
                response = await client.get(**params)

                responses.append(response)

        web_search_results = self._parse_responses(responses, debug)
        
        print(f"Google Search Results length: {len(web_search_results)}")
        
        if debug:
            for result in web_search_results:
                print(result.model_dump_json(indent=2))
        return web_search_results

    def _parse_responses(
        self, responses: list[Response], debug: bool = False
    ) -> list[WebSearchResult]:
        results = []
        for response in responses:
            results.extend(self._extract_urls(response, debug))
        return results

    def _extract_urls(
        self, response: Response, debug: bool = False
    ) -> list[WebSearchResult]:
        """Clean the response from the search engine."""
        results = response.json()

        if debug:
            print(f"Google Search Response length: {len(results)}")
            print(f"Google Search Response Keys: {results.keys()}")

        links = [
            WebSearchResult(
                url=item["link"],
                snippet=item["snippet"],
                title=item.get("title", item.get("htmlTitle", "")),
            )
            for item in results["items"]
        ]
        return links
