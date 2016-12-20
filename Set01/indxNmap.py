from elasticsearch import Elasticsearch




def createindex(elasobj, indexname):
    elasobj.indices.create(
        index=indexname,
        body={
  "settings": {
    "index": {
      "store": {
        "type": "default"
      },
      "number_of_shards": 1,
      "number_of_replicas": 0
    },
    "analysis": {
      "analyzer": {
        "my_english": { 
          "type": "english",
          "stopwords_path": "stopwords.txt" 
        }
      }
    }
  }
}
)


def putmapping(elasobj, indexname):
    elasobj.indices.put_mapping(
        index=indexname,
        doc_type='document',
        body={
  "document": {
    "properties": {
      "docno": {
        "type": "string",
        "store": "true",
        "index": "not_analyzed"
      },
      "text": {
        "type": "string",
        "store": "true",
        "index": "analyzed",
        "term_vector": "with_positions_offsets_payloads",
        "analyzer": "my_english"
      }
    }
  }
})



def main():
createindex(elasrch, "ap_89")
putmapping(elasrch, "ap_89")


if __name__ == '__main__':
    # Create a elasticsearch object by connecting at localhost:9200
    elasrch = Elasticsearch(
        "localhost:9200", timeout=600, max_retries=10, revival_delay=0)
    main()
