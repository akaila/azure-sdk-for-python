# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    PREVIEW (api version 2026-05-01-preview): this sample uses APIs that are
    not yet in a stable release. Behavior may change before GA.

    Demonstrates the preview-only configuration knobs on a knowledge base:
    CORS options, the new GPT-5.x answer-synthesis model names, retrieval
    defaults (output mode and reasoning effort), and a knowledge source
    reference that opts into the new image-serving default.

USAGE:
    python sample_knowledge_base_configuration_preview.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
        (e.g., https://<your-search-service-name>.search.windows.net)
    2) AZURE_SEARCH_INDEX_NAME - target search index name (e.g., "hotels-sample-index").
        The index must have a semantic configuration.
    3) AZURE_SEARCH_API_KEY - the admin key for your search service
    4) SAMPLE_RUN_TAG - (optional) unique prefix used for all resources this run
        creates so they cannot collide with other samples or users on a shared
        service. Defaults to a timestamp.
"""

import datetime
import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]

run_tag = os.environ.get("SAMPLE_RUN_TAG") or datetime.datetime.utcnow().strftime(
    "samplerun-%Y%m%d-%H%M%S"
)
knowledge_source_name = f"{run_tag}-kbcfg-ks"
knowledge_base_name = f"{run_tag}-kbcfg-kb"


def create_knowledge_base_with_preview_configuration():
    # [START create_knowledge_base_with_preview_configuration]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import ApiVersion
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        AzureOpenAIModelName,
        AzureOpenAIVectorizerParameters,
        CorsOptions,
        KnowledgeBase,
        KnowledgeBaseAzureOpenAIModel,
        KnowledgeSourceReference,
        SearchIndexKnowledgeSource,
        SearchIndexKnowledgeSourceParameters,
    )
    from azure.search.documents.knowledgebases.models import (
        KnowledgeRetrievalMinimalReasoningEffort,
        KnowledgeRetrievalOutputMode,
    )

    index_client = SearchIndexClient(
        service_endpoint,
        AzureKeyCredential(key),
        api_version=ApiVersion.V2026_05_01_PREVIEW,
    )

    index_client.create_or_update_knowledge_source(
        knowledge_source=SearchIndexKnowledgeSource(
            name=knowledge_source_name,
            search_index_parameters=SearchIndexKnowledgeSourceParameters(
                search_index_name=index_name,
            ),
        )
    )

    knowledge_base = KnowledgeBase(
        name=knowledge_base_name,
        description="Preview configuration sample: CORS, GPT-5.x model, retrieval defaults.",
        knowledge_sources=[
            KnowledgeSourceReference(
                name=knowledge_source_name,
                enable_image_serving=False,
            ),
        ],
        cors_options=CorsOptions(
            allowed_origins=["https://contoso.example"],
            max_age_in_seconds=300,
        ),
        models=[
            KnowledgeBaseAzureOpenAIModel(
                azure_open_ai_parameters=AzureOpenAIVectorizerParameters(
                    resource_url="https://contoso.openai.azure.com",
                    deployment_name="gpt-5-4-mini-deployment",
                    model_name=AzureOpenAIModelName.GPT_5_4_MINI,
                ),
            ),
        ],
        output_mode=KnowledgeRetrievalOutputMode.EXTRACTIVE_DATA,
        retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
    )

    result = index_client.create_or_update_knowledge_base(knowledge_base=knowledge_base)
    print(f"Created: knowledge base '{result.name}'")
    print(f"  output_mode default: {result.output_mode}")
    print(f"  cors allowed_origins: {result.cors_options.allowed_origins}")
    print(f"  models[0] kind: {result.models[0].kind}")
    # [END create_knowledge_base_with_preview_configuration]


def cleanup():
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import ResourceNotFoundError
    from azure.search.documents import ApiVersion
    from azure.search.documents.indexes import SearchIndexClient

    index_client = SearchIndexClient(
        service_endpoint,
        AzureKeyCredential(key),
        api_version=ApiVersion.V2026_05_01_PREVIEW,
    )
    for name, delete in [
        (knowledge_base_name, index_client.delete_knowledge_base),
        (knowledge_source_name, index_client.delete_knowledge_source),
    ]:
        try:
            delete(name)
            print(f"Deleted: {name}")
        except ResourceNotFoundError:
            pass


if __name__ == "__main__":
    try:
        create_knowledge_base_with_preview_configuration()
    finally:
        cleanup()