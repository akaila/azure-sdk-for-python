# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    PREVIEW (api version 2026-05-01-preview): this sample uses APIs that are
    not yet in a stable release. Behavior may change before GA.

    Async version of sample_knowledge_retrieval_response_preview.py.

USAGE:
    python sample_knowledge_retrieval_response_preview_async.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_INDEX_NAME - target search index name with a semantic configuration
    3) AZURE_SEARCH_API_KEY - the admin key for your search service
    4) SAMPLE_RUN_TAG - (optional) unique prefix for created resources
"""

import asyncio
import datetime
import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]

run_tag = os.environ.get("SAMPLE_RUN_TAG") or datetime.datetime.utcnow().strftime(
    "samplerun-%Y%m%d-%H%M%S"
)
knowledge_source_name = f"{run_tag}-retr-ks"
knowledge_base_name = f"{run_tag}-retr-kb"


async def setup():
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import ApiVersion
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        KnowledgeBase,
        KnowledgeSourceReference,
        SearchIndexKnowledgeSource,
        SearchIndexKnowledgeSourceParameters,
    )
    from azure.search.documents.knowledgebases.models import KnowledgeRetrievalMinimalReasoningEffort

    async with SearchIndexClient(
        service_endpoint,
        AzureKeyCredential(key),
        api_version=ApiVersion.V2026_05_01_PREVIEW,
    ) as index_client:
        await index_client.create_or_update_knowledge_source(
            knowledge_source=SearchIndexKnowledgeSource(
                name=knowledge_source_name,
                search_index_parameters=SearchIndexKnowledgeSourceParameters(
                    search_index_name=index_name,
                ),
            )
        )
        await index_client.create_or_update_knowledge_base(
            knowledge_base=KnowledgeBase(
                name=knowledge_base_name,
                knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
                retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
            )
        )


async def retrieve_with_preview_response_fields():
    # [START retrieve_with_preview_response_fields_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import ApiVersion
    from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalMinimalReasoningEffort,
        KnowledgeRetrievalOutputMode,
        KnowledgeRetrievalSemanticIntent,
    )

    async with KnowledgeBaseRetrievalClient(
        service_endpoint,
        credential=AzureKeyCredential(key),
        knowledge_base_name=knowledge_base_name,
        api_version=ApiVersion.V2026_05_01_PREVIEW,
    ) as retrieval_client:
        request = KnowledgeBaseRetrievalRequest(
            intents=[KnowledgeRetrievalSemanticIntent(search="luxury hotels in Seattle")],
            max_output_documents=3,
            include_activity=True,
            output_mode=KnowledgeRetrievalOutputMode.EXTRACTIVE_DATA,
            retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
        )

        result = await retrieval_client.retrieve(request)

        for record in result.activity or []:
            model_name = getattr(record, "model_name", None)
            if model_name:
                print(f"activity[{record.id}] type={record.type} model_name={model_name}")

        for ref in result.references or []:
            label = getattr(ref, "search_sensitivity_label_info", None)
            if label is not None:
                print(
                    f"reference[{ref.id}] purview_label="
                    f"{label.display_name or label.sensitivity_label_id}"
                )

        response_label = result.response_sensitivity_label_info
        if response_label is not None:
            print(
                "response sensitivity label: "
                f"{response_label.display_name or response_label.sensitivity_label_id}"
            )

        print(f"references returned: {len(result.references or [])}")
    # [END retrieve_with_preview_response_fields_async]


async def retrieve_with_answer_synthesis():
    openai_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    openai_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
    if not (openai_endpoint and openai_deployment):
        print(
            "skipping answer_synthesis demo: set AZURE_OPENAI_ENDPOINT and "
            "AZURE_OPENAI_DEPLOYMENT_NAME to enable."
        )
        return

    # [START retrieve_with_answer_synthesis_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import ApiVersion
    from azure.search.documents.indexes.aio import SearchIndexClient
    from azure.search.documents.indexes.models import (
        AzureOpenAIVectorizerParameters,
        KnowledgeBase,
        KnowledgeBaseAzureOpenAIModel,
        KnowledgeSourceReference,
    )
    from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalOutputMode,
        KnowledgeRetrievalSemanticIntent,
    )

    async with SearchIndexClient(
        service_endpoint,
        AzureKeyCredential(key),
        api_version=ApiVersion.V2026_05_01_PREVIEW,
    ) as index_client:
        await index_client.create_or_update_knowledge_base(
            knowledge_base=KnowledgeBase(
                name=knowledge_base_name,
                knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
                models=[
                    KnowledgeBaseAzureOpenAIModel(
                        azure_open_ai_parameters=AzureOpenAIVectorizerParameters(
                            resource_url=openai_endpoint,
                            deployment_name=openai_deployment,
                            model_name=openai_deployment,
                        ),
                    ),
                ],
            )
        )

    async with KnowledgeBaseRetrievalClient(
        service_endpoint,
        credential=AzureKeyCredential(key),
        knowledge_base_name=knowledge_base_name,
        api_version=ApiVersion.V2026_05_01_PREVIEW,
    ) as retrieval_client:
        request = KnowledgeBaseRetrievalRequest(
            intents=[KnowledgeRetrievalSemanticIntent(search="luxury hotels in Seattle")],
            output_mode=KnowledgeRetrievalOutputMode.ANSWER_SYNTHESIS,
        )

        result = await retrieval_client.retrieve(request)
        for message in result.response or []:
            for content in message.content or []:
                text = getattr(content, "text", None)
                if text:
                    print(f"synthesized: {text}")
    # [END retrieve_with_answer_synthesis_async]


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
        await setup()
        await retrieve_with_preview_response_fields()
        await retrieve_with_answer_synthesis()
    finally:
        await cleanup()


if __name__ == "__main__":
    asyncio.run(main())