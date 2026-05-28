# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    PREVIEW (api version 2026-05-01-preview): this sample uses APIs that are
    not yet in a stable release. Behavior may change before GA.

    Async version of sample_knowledge_source_fabric_data_agent_preview.py.

USAGE:
    python sample_knowledge_source_fabric_data_agent_preview_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
    3) AZURE_FABRIC_WORKSPACE_ID - Fabric workspace id holding the data agent
    4) AZURE_FABRIC_DATA_AGENT_ID - data agent id within the workspace
    5) SAMPLE_RUN_TAG - (optional) unique prefix for created resources
"""

import asyncio
import datetime
import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]
fabric_workspace_id = os.environ["AZURE_FABRIC_WORKSPACE_ID"]
fabric_data_agent_id = os.environ["AZURE_FABRIC_DATA_AGENT_ID"]

run_tag = os.environ.get("SAMPLE_RUN_TAG") or datetime.datetime.utcnow().strftime(
    "samplerun-%Y%m%d-%H%M%S"
)
knowledge_source_name = f"{run_tag}-fabagent-ks"
knowledge_base_name = f"{run_tag}-fabagent-kb"


async def create_fabric_data_agent_knowledge_source_and_attach():
    # [START create_fabric_data_agent_knowledge_source_and_attach_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import ApiVersion
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        FabricDataAgentKnowledgeSource,
        FabricDataAgentKnowledgeSourceParameters,
        KnowledgeBase,
        KnowledgeSourceReference,
    )

    async with SearchIndexClient(
        service_endpoint,
        AzureKeyCredential(key),
        api_version=ApiVersion.V2026_05_01_PREVIEW,
    ) as index_client:
        result = await index_client.create_or_update_knowledge_source(
            knowledge_source=FabricDataAgentKnowledgeSource(
                name=knowledge_source_name,
                description="Fabric data agent knowledge source created by preview sample.",
                fabric_data_agent_parameters=FabricDataAgentKnowledgeSourceParameters(
                    workspace_id=fabric_workspace_id,
                    data_agent_id=fabric_data_agent_id,
                ),
            )
        )
        print(f"Created: knowledge source '{result.name}' kind={result.kind}")

        await index_client.create_or_update_knowledge_base(
            knowledge_base=KnowledgeBase(
                name=knowledge_base_name,
                knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
            )
        )
    # [END create_fabric_data_agent_knowledge_source_and_attach_async]


async def get_and_retrieve_source():
    # [START get_fabric_data_agent_knowledge_source_and_retrieve_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError
    from azure.search.documents import ApiVersion
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalSemanticIntent,
    )

    async with SearchIndexClient(
        service_endpoint,
        AzureKeyCredential(key),
        api_version=ApiVersion.V2026_05_01_PREVIEW,
    ) as index_client:
        fetched = await index_client.get_knowledge_source(knowledge_source_name)
        print(f"Got: knowledge source '{fetched.name}' kind={fetched.kind}")

    async with KnowledgeBaseRetrievalClient(
        service_endpoint,
        credential=AzureKeyCredential(key),
        knowledge_base_name=knowledge_base_name,
        api_version=ApiVersion.V2026_05_01_PREVIEW,
    ) as retrieval_client:
        request = KnowledgeBaseRetrievalRequest(
            intents=[KnowledgeRetrievalSemanticIntent(search="summary from the data agent")],
            include_activity=True,
        )

        try:
            result = await retrieval_client.retrieve(request)
        except HttpResponseError as e:
            print(f"retrieve attempted; service returned: {e.message}")
            return

        print(f"references returned: {len(result.references or [])}")
        for ref in (result.references or [])[:3]:
            print(f"  reference: type={type(ref).__name__}")
        print(f"activity entries: {len(result.activity or [])}")
        for act in (result.activity or [])[:3]:
            print(f"  activity: type={type(act).__name__}")
    # [END get_fabric_data_agent_knowledge_source_and_retrieve_async]


async def cleanup():
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import ResourceNotFoundError
    from azure.search.documents import ApiVersion
    from azure.search.documents.indexes.aio import SearchIndexClient

    async with SearchIndexClient(
        service_endpoint,
        AzureKeyCredential(key),
        api_version=ApiVersion.V2026_05_01_PREVIEW,
    ) as index_client:
        for name, delete in [
            (knowledge_base_name, index_client.delete_knowledge_base),
            (knowledge_source_name, index_client.delete_knowledge_source),
        ]:
            try:
                await delete(name)
                print(f"Deleted: {name}")
            except ResourceNotFoundError:
                pass


async def main():
    try:
        await create_fabric_data_agent_knowledge_source_and_attach()
        await get_and_retrieve_source()
    finally:
        await cleanup()


if __name__ == "__main__":
    asyncio.run(main())
