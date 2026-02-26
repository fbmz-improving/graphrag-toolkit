## Lexical Graph

The lexical-graph package provides a framework for automating the construction of a [hierarchical lexical graph](../docs/lexical-graph/graph-model.md) from unstructured data, and composing question-answering strategies that query this graph when answering user questions.

### Features

  - Built-in graph store support for [Amazon Neptune Analytics](https://docs.aws.amazon.com/neptune-analytics/latest/userguide/what-is-neptune-analytics.html), [Amazon Neptune Database](https://docs.aws.amazon.com/neptune/latest/userguide/intro.html), and [Neo4j](https://neo4j.com/docs/).
  - Built-in vector store support for Neptune Analytics, [Amazon OpenSearch Serverless](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless.html), [Amazon S3 Vectors](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors.html) and Postgres with the pgvector extension.
  - Built-in support for foundation models (LLMs and embedding models) on [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/).
  - Easily extended to support additional graph and vector stores and model backends.
  - [Multi-tenancy](../docs/lexical-graph/multi-tenancy.md) – multiple separate lexical graphs in the same underlying graph and vector stores.
  - Continuous ingest and [batch extraction](../docs/lexical-graph/batch-extraction.md) (using [Bedrock batch inference](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference.html)) modes.
  - [Versioned updates](../docs/lexical-graph/versioned-updates.md) for updating source documents and querying the state of the graph and vector stores at a point in time.
  - Quickstart [AWS CloudFormation templates](../examples/lexical-graph/cloudformation-templates/) for Neptune Database, OpenSearch Serverless, and Amazon Aurora Postgres.

## Installation

The lexical-graph requires Python 3.10 or greater and [pip](http://www.pip-installer.org/en/latest/).

Install from the latest release tag:

```
$ pip install https://github.com/awslabs/graphrag-toolkit/archive/refs/tags/v3.16.2.zip#subdirectory=lexical-graph
```

Or install from the `main` branch to get the latest changes:

```
$ pip install https://github.com/awslabs/graphrag-toolkit/archive/refs/heads/main.zip#subdirectory=lexical-graph
```

If you're running on AWS, you must run your application in an AWS region containing the Amazon Bedrock foundation models used by the lexical graph (see the [configuration](../docs/lexical-graph/configuration.md#graphragconfig) section in the documentation for details on the default models used), and must [enable access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) to these models before running any part of the solution.

### Additional dependencies

You will need to install additional dependencies for specific graph and vector store backends:

#### Amazon OpenSearch Serverless

```bash
$ pip install opensearch-py llama-index-vector-stores-opensearch
```

#### Postgres with pgvector

```bash
$ pip install psycopg2-binary pgvector
```

#### Amazon S3 Vectors

```bash
$ pip install boto3
```

#### Neo4j

``` bash
$ pip install neo4j
```

### Connection strings

Pass a connection string to `GraphStoreFactory.for_graph_store()` or `VectorStoreFactory.for_vector_store()` to select a backend:

| Store | Connection string |
| --- | --- |
| Neptune Analytics (graph) | `neptune-graph://<graph-id>` |
| Neptune Database (graph) | `neptune-db://<hostname>` or any hostname ending `.neptune.amazonaws.com` |
| Neo4j (graph) | `bolt://`, `bolt+ssc://`, `bolt+s://`, `neo4j://`, `neo4j+ssc://`, or `neo4j+s://` URLs |
| OpenSearch Serverless (vector) | `aoss://<url>` |
| Neptune Analytics (vector) | `neptune-graph://<graph-id>` |
| pgvector (vector) | constructed via `PGVectorIndexFactory` |
| S3 Vectors (vector) | constructed via `S3VectorIndexFactory` |
| Dummy / no-op | `None` or any unrecognised string — falls back to `DummyGraphStore` / `DummyVectorIndex` |

## Example of use

### Indexing

```python
from graphrag_toolkit.lexical_graph import LexicalGraphIndex
from graphrag_toolkit.lexical_graph.storage import GraphStoreFactory
from graphrag_toolkit.lexical_graph.storage import VectorStoreFactory

# requires pip install llama-index-readers-web
from llama_index.readers.web import SimpleWebPageReader

def run_extract_and_build():

    with (
        GraphStoreFactory.for_graph_store(
            'neptune-db://my-graph.cluster-abcdefghijkl.us-east-1.neptune.amazonaws.com'
        ) as graph_store,
        VectorStoreFactory.for_vector_store(
            'aoss://https://abcdefghijkl.us-east-1.aoss.amazonaws.com'
        ) as vector_store
    ):

        graph_index = LexicalGraphIndex(
            graph_store,
            vector_store
        )

        doc_urls = [
            'https://docs.aws.amazon.com/neptune/latest/userguide/intro.html',
            'https://docs.aws.amazon.com/neptune-analytics/latest/userguide/what-is-neptune-analytics.html',
            'https://docs.aws.amazon.com/neptune-analytics/latest/userguide/neptune-analytics-features.html',
            'https://docs.aws.amazon.com/neptune-analytics/latest/userguide/neptune-analytics-vs-neptune-database.html'
        ]

        docs = SimpleWebPageReader(
            html_to_text=True,
            metadata_fn=lambda url:{'url': url}
        ).load_data(doc_urls)

        graph_index.extract_and_build(docs, show_progress=True)

if __name__ == '__main__':
    run_extract_and_build()
```

### Querying

```python
from graphrag_toolkit.lexical_graph import LexicalGraphQueryEngine
from graphrag_toolkit.lexical_graph.storage import GraphStoreFactory
from graphrag_toolkit.lexical_graph.storage import VectorStoreFactory

def run_query():

    with (
        GraphStoreFactory.for_graph_store(
            'neptune-db://my-graph.cluster-abcdefghijkl.us-east-1.neptune.amazonaws.com'
        ) as graph_store,
        VectorStoreFactory.for_vector_store(
            'aoss://https://abcdefghijkl.us-east-1.aoss.amazonaws.com'
        ) as vector_store
    ):

        query_engine = LexicalGraphQueryEngine.for_traversal_based_search(
            graph_store,
            vector_store
        )

        response = query_engine.query('''What are the differences between Neptune Database
                                         and Neptune Analytics?''')

        print(response.response)

if __name__ == '__main__':
    run_query()
```

## Documentation

  - [Overview](../docs/lexical-graph/overview.md)
  - [Graph Model](../docs/lexical-graph/graph-model.md)
  - [Storage Model](../docs/lexical-graph/storage-model.md)
  - [Indexing](../docs/lexical-graph/indexing.md)
    - [Batch Extraction](../docs/lexical-graph/batch-extraction.md)
    - [Configuring Batch Extraction](../docs/lexical-graph/configuring-batch-extraction.md)
    - [Versioned Updates](../docs/lexical-graph/versioned-updates.md)
  - [Querying](../docs/lexical-graph/querying.md)
    - [Traversal-Based Search](../docs/lexical-graph/traversal-based-search.md)
    - [Traversal-Based Search Configuration](../docs/lexical-graph/traversal-based-search-configuration.md)
  - [Configuration](../docs/lexical-graph/configuration.md)
  - [Security](../docs/lexical-graph/security.md)
  - [FAQ](../docs/lexical-graph/faq.md)


## Suggested Future Enhancements

Here are several points that could be added to improve the [`prompt_provider_config.py`](./src/graphrag_toolkit/lexical_graph/prompts/prompt_provider_config.py)

### 1. Unified PromptProviderRegistry or Factory

- Introduce a registry that maps provider types to config classes, e.g.:

  ```python
  registry = {
      "static": StaticPromptProviderConfig,
      "file": FilePromptProviderConfig,
      "s3": S3PromptProviderConfig,
      "bedrock": BedrockPromptProviderConfig
  }
  ```

- Enable initialization from a config dict: `registry[type](**params).build()`

### 2. Config Serialization

- Add `.to_dict()` and `.from_dict()` methods to each config class for CLI/JSON compatibility.
- Useful for web UIs or YAML-driven orchestration.

### 3. Validation & Type Enforcement

- Use Pydantic or `__post_init__()` methods to validate inputs (e.g., ARN format, S3 bucket name).
- Example: validate AWS region format or prompt ARN prefix.

### 4. Logging Enhancements

- Add verbose logging on each provider (e.g., which prompt path or ARN was loaded).
- Include diagnostics for STS calls and client creation failures.

### 5. Caching Layer

- Cache resolved prompt text in memory or on disk (especially for S3 and Bedrock).
- Avoid unnecessary repeated fetches in batch queries.

### 6. Runtime Provider Switching

- Allow query-time override of prompt provider (e.g., via `query_engine.query(..., prompt_provider=...)`).
- Enables experimentation with different prompt strategies.

### 7. Prompt Fallback Strategy

- Support fallback to defaults or static provider if S3/Bedrock fails.
- Enables robust operation in partially degraded environments.

### 8. Custom Prompt Variables

- Support variable interpolation in prompt templates (e.g., using `{tenant_id}` or `{user_role}`).
- Useful for multi-tenant or role-specific prompting.

### 9. Multi-Language Prompt Support

- Load prompt variants based on locale/language code.
- Supports internationalization of RAG applications.

### 10. Bedrock Caching with Prompt Versioning

- Cache based on `(ARN, version)` tuple.
- Useful when managing multiple versions in experiments or A/B testing.

## License

This project is licensed under the Apache-2.0 License.
