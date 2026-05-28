# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    PREVIEW (api version 2026-05-01-preview): this sample uses APIs that are
    not yet in a stable release. Behavior may change before GA.

    Creates a "file" knowledge source. File knowledge sources let you point a
    knowledge base at content you upload directly to the service; the service
    manages an internal index for the uploaded content.

USAGE:
    python sample_knowledge_source_file_preview.py

    Set the following environment variables before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - base URL of your Azure AI Search service
    2) AZURE_SEARCH_API_KEY - the admin key for your search service
    3) SAMPLE_RUN_TAG - (optional) unique prefix for created resources
"""

import datetime
import os

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
key = os.environ["AZURE_SEARCH_API_KEY"]

run_tag = os.environ.get("SAMPLE_RUN_TAG") or datetime.datetime.utcnow().strftime(
    "samplerun-%Y%m%d-%H%M%S"
)
knowledge_source_name = f"{run_tag}-file-ks"
knowledge_base_name = f"{run_tag}-file-kb"


def create_file_knowledge_source_and_attach():
    # [START create_file_knowledge_source_and_attach]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import ApiVersion
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        FileKnowledgeSource,
        FileKnowledgeSourceParameters,
        KnowledgeBase,
        KnowledgeSourceContentExtractionMode,
        KnowledgeSourceReference,
    )
    from azure.search.documents.knowledgebases.models import (
        KnowledgeSourceIngestionParameters,
        KnowledgeRetrievalMinimalReasoningEffort,
    )

    index_client = SearchIndexClient(
        service_endpoint,
        AzureKeyCredential(key),
        api_version=ApiVersion.V2026_05_01_PREVIEW,
    )

    result = index_client.create_or_update_knowledge_source(
        knowledge_source=FileKnowledgeSource(
            name=knowledge_source_name,
            description="File-backed knowledge source created by preview sample.",
            file_parameters=FileKnowledgeSourceParameters(
                ingestion_parameters=KnowledgeSourceIngestionParameters(
                    content_extraction_mode=KnowledgeSourceContentExtractionMode.MINIMAL,
                ),
            ),
        )
    )
    print(f"Created: knowledge source '{result.name}' kind={result.kind}")

    index_client.create_or_update_knowledge_base(
        knowledge_base=KnowledgeBase(
            name=knowledge_base_name,
            knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
            retrieval_reasoning_effort=KnowledgeRetrievalMinimalReasoningEffort(),
        )
    )
    # [END create_file_knowledge_source_and_attach]


def get_and_retrieve_source():
    # [START get_file_knowledge_source_and_retrieve]
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError
    from azure.search.documents import ApiVersion
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
    from azure.search.documents.knowledgebases.models import (
        KnowledgeBaseRetrievalRequest,
        KnowledgeRetrievalSemanticIntent,
    )

    index_client = SearchIndexClient(
        service_endpoint,
        AzureKeyCredential(key),
        api_version=ApiVersion.V2026_05_01_PREVIEW,
    )

    fetched = index_client.get_knowledge_source(knowledge_source_name)
    print(f"Got: knowledge source '{fetched.name}' kind={fetched.kind}")

    retrieval_client = KnowledgeBaseRetrievalClient(
        service_endpoint,
        credential=AzureKeyCredential(key),
        knowledge_base_name=knowledge_base_name,
        api_version=ApiVersion.V2026_05_01_PREVIEW,
    )
    request = KnowledgeBaseRetrievalRequest(
        intents=[KnowledgeRetrievalSemanticIntent(search="example query for uploaded files")],
        include_activity=True,
    )

    try:
        result = retrieval_client.retrieve(request)
    except HttpResponseError as e:
        print(f"retrieve attempted; service returned: {e.message}")
        return

    print(f"references returned: {len(result.references or [])}")
    for ref in (result.references or [])[:3]:
        print(f"  reference: type={type(ref).__name__}")
    print(f"activity entries: {len(result.activity or [])}")
    for act in (result.activity or [])[:3]:
        print(f"  activity: type={type(act).__name__}")
    # [END get_file_knowledge_source_and_retrieve]


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
        create_file_knowledge_source_and_attach()
        get_and_retrieve_source()
    finally:
        cleanup()