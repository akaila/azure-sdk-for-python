# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    PREVIEW (api version 2026-05-01-preview): this sample uses APIs that are
    not yet in a stable release. Behavior may change before GA.

    Shows two preview-only knobs on KnowledgeSourceReference:
      * enable_freshness: turn on freshness scoring for results from a source.
      * enable_image_serving: opt a source in or out of image content.

    Both are configured at attach time on the knowledge base, and apply during
    retrieve unless overridden by a per-call knowledge_source_params entry.

USAGE:
    python sample_knowledge_source_freshness_preview.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_INDEX_NAME - target search index name with a semantic configuration
    3) AZURE_SEARCH_API_KEY - the admin key for your search service
    4) SAMPLE_RUN_TAG - (optional) unique prefix for created resources
"""

import datetime
import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]

run_tag = os.environ.get("SAMPLE_RUN_TAG") or datetime.datetime.utcnow().strftime(
    "samplerun-%Y%m%d-%H%M%S"
)
knowledge_source_name = f"{run_tag}-fresh-ks"
knowledge_base_name = f"{run_tag}-fresh-kb"


def attach_source_with_freshness_defaults():
    # [START attach_source_with_freshness_defaults]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import ApiVersion
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        KnowledgeBase,
        KnowledgeSourceReference,
        SearchIndexKnowledgeSource,
        SearchIndexKnowledgeSourceParameters,
    )
    from azure.search.documents.knowledgebases.models import KnowledgeRetrievalMinimalReasoningEffort

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

    index_client.create_or_update_knowledge_base(
        knowledge_base=KnowledgeBase(
            name=knowledge_base_name,
            knowledge_sources=[
                KnowledgeSourceReference(
                    name=knowledge_source_name,
                    enable_freshness=True,
                    enable_image_serving=False,
                ),
            ],
            retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
        )
    )
    # [END attach_source_with_freshness_defaults]


def retrieve_using_attach_time_defaults():
    # [START retrieve_using_attach_time_defaults]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import ApiVersion
    from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalSemanticIntent,
    )

    retrieval_client = KnowledgeBaseRetrievalClient(
        service_endpoint,
        credential=AzureKeyCredential(key),
        knowledge_base_name=knowledge_base_name,
        api_version=ApiVersion.V2026_05_01_PREVIEW,
    )

    request = KnowledgeBaseRetrievalRequest(
        intents=[KnowledgeRetrievalSemanticIntent(search="recent hotel configuration guidance")],
    )

    result = retrieval_client.retrieve(request)
    print(f"references returned: {len(result.references or [])}")
    # [END retrieve_using_attach_time_defaults]


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
        attach_source_with_freshness_defaults()
        retrieve_using_attach_time_defaults()
    finally:
        cleanup()