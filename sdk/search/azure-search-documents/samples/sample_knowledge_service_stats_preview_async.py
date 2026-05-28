# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    PREVIEW (api version 2026-05-01-preview): this sample uses APIs that are
    not yet in a stable release. Behavior may change before GA.

    Async version of sample_knowledge_service_stats_preview.py.

USAGE:
    python sample_knowledge_service_stats_preview_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
"""

import asyncio
import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]


async def show_knowledge_resource_counters():
    # [START show_knowledge_resource_counters_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import ApiVersion
    from azure.search.documents.indexes.aio import SearchIndexClient

    async with SearchIndexClient(
        service_endpoint,
        AzureKeyCredential(key),
        api_version=ApiVersion.V2026_05_01_PREVIEW,
    ) as index_client:
        stats = await index_client.get_service_statistics()
        counters = stats.counters

        def fmt(counter):
            quota = counter.quota if counter.quota is not None else "unlimited"
            return f"{counter.usage} / {quota}"

        print(f"knowledge bases:   {fmt(counters.knowledge_base_counter)}")
        print(f"knowledge sources: {fmt(counters.knowledge_source_counter)}")
        print(f"indexes:           {fmt(counters.index_counter)}")
        print(f"indexers:          {fmt(counters.indexer_counter)}")
    # [END show_knowledge_resource_counters_async]


if __name__ == "__main__":
    asyncio.run(show_knowledge_resource_counters())