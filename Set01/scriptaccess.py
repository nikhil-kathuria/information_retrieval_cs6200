from elasticsearch import Elasticsearch


def explaintrue():
    jsonbody = {"query": {"match": {"text": "nuclear"}}, "explain": 'true'}
    response = elasrch.search(index='ap_89', doc_type="document", body=jsonbody, size=10)
    print(response)


def scriptcall():
    script = ""
    jsonbody = {}


def main():
    explaintrue()


if __name__ == '__main__':
    # Create a elasticsearch object by connecting at localhost:9200
    elasrch = Elasticsearch(
        "localhost:9200", timeout=600, max_retries=10, revival_delay=0)
    main()
