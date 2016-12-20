import org.elasticsearch.action.count.CountResponse;
import org.elasticsearch.action.search.SearchResponse;
import org.elasticsearch.client.Client;
import org.elasticsearch.common.unit.TimeValue;
import org.elasticsearch.common.xcontent.*;
import org.elasticsearch.index.query.QueryBuilder;
import org.elasticsearch.index.query.QueryBuilder.*;
import org.elasticsearch.index.query.QueryBuilders;
import org.elasticsearch.node.Node;
import org.elasticsearch.search.SearchHit;
import org.elasticsearch.search.aggregations.AggregationBuilders;
import org.elasticsearch.search.aggregations.metrics.MetricsAggregationBuilder;
import org.elasticsearch.search.aggregations.metrics.cardinality.Cardinality;
import org.elasticsearch.search.facet.statistical.StatisticalFacet;

import java.io.*;
import java.util.*;

import static org.elasticsearch.node.NodeBuilder.nodeBuilder;
import static org.elasticsearch.index.query.FilterBuilders.*;
import static org.elasticsearch.index.query.QueryBuilders.*;

public class RunQuery {
    public static void main(String[] args) throws IOException {
	        if (args.length != 1) {
	            throw new IllegalArgumentException("Only Need config file.");
	        }

	        Config config = new Config(args[0]);
		// starts client
		Node node = nodeBuilder().client(true).clusterName(clusterName).node();
		Client client = node.client();


    }

    /**
     * V is the vocabulary size – the total number of unique terms in the collection.
     * @param client
     * @param index
     * @param type
     * @param field
     * @return
     */
    private static long getVocabularySize(Client client, String index, String type, String field) {
        MetricsAggregationBuilder aggregation =
                AggregationBuilders
	    .cardinality("agg")
	    .field(field);
        SearchResponse sr = client.prepareSearch(index).setTypes(type)
	    .addAggregation(aggregation)
	    .execute().actionGet();

        Cardinality agg = sr.getAggregations().get("agg");
        long value = agg.getValue();
        return value;

    }

    /**
     * return Pairs of <"decno", tf value> by given term query.
     * @param client
     * @param qb
     * @param index
     * @param type
     * @return
     */
    public static Map<String, Integer> queryTF(Client client, QueryBuilder qb, String index, String type) {
        SearchResponse scrollResp = client.prepareSearch(index).setTypes(type)
	    .setScroll(new TimeValue(6000))
	    .setQuery(qb)
	    .setExplain(true)
	    .setSize(1000).execute().actionGet();

        // no query matched
        if (scrollResp.getHits().getTotalHits() == 0) {
            return new HashMap<String, Integer>();
        }
        Map<String, Integer> results = new HashMap<>();
        while (true) {
            for (SearchHit hit : scrollResp.getHits().getHits()) {
                String docno = (String) hit.getSource().get("docno");
                int tf =  (int) hit.getExplanation().getDetails()[0].getDetails()[0].getDetails()[0].getValue();
                results.put(docno, tf);
            }
            scrollResp =
		client.prepareSearchScroll(scrollResp.getScrollId()).setScroll(
									       new TimeValue(6000)).execute().actionGet();
            if (scrollResp.getHits().getHits().length == 0) {
                break;
            }
        }
        return results;
    }
    /**
     * get statistical facet by given docno or whole documents
     * INFO including following:
     "facets": {
        "text": {
             "_type": "statistical",
             "count": 84678,
             "total": 18682561,
             "min": 0,
             "max": 802,
             "mean": 220.63063605659084,
             "sum_of_squares": 4940491417,
             "variance": 9666.573376838636,
             "std_deviation": 98.31873360066552
        }
     }
     * @param client
     * @param index
     * @param type
     * @param matchedField
     * @param matchedValue
     * @return
     * @throws IOException
     */
    private static StatisticalFacet getStatsOnTextTerms(Client client, String index, String type, String matchedField, String matchedValue) throws IOException {
        XContentBuilder facetsBuilder;
        if (matchedField == null && matchedValue == null) {    // match_all docs
            facetsBuilder = getStatsTermsBuilder();
        }
        else {
            facetsBuilder = getStatsTermsByMatchFieldBuilder(matchedField, matchedValue);
        }
        SearchResponse response = client.prepareSearch(index).setTypes(type)
	    .setSource(facetsBuilder)
	    .execute()
	    .actionGet();
        StatisticalFacet f = (StatisticalFacet) response.getFacets().facetsAsMap().get("text");
        return f;
    }




    /**
     * builder for facets statistical terms length by given matched field, like docno.
     * In Sense:
     *
     POST ap_dataset/document/_search
     {
        "query": {
             "match": {
                 "docno": "AP891216-0142"
            }
        },
        "facets": {
            "text": {
                "statistical": {
                    "script": "doc['text'].values.size()"
                }
            }
        }
     }
     * @param matchField
     * @param matchValue
     * @return
     * @throws IOException
     */
    private static XContentBuilder getStatsTermsByMatchFieldBuilder(String matchField, String matchValue) throws IOException {
        XContentBuilder builder = XContentFactory.jsonBuilder();
        builder.startObject()
	    .startObject("query")
	    .startObject("match")
	    .field(matchField, matchValue)
	    .endObject()
	    .endObject()
	    .startObject("facets")
	    .startObject("text")
	    .startObject("statistical")
	    .field("script", "doc['text'].values.size()")
	    .endObject()
	    .endObject()
	    .endObject()
	    .endObject();
        return builder;
    }

    /**
     * builder for the facets statistical terms length by whole documents.
     * In Sense:
     * POST /ap_dataset/document/_search
        {
         "query": {"match_all": {}},
            "facets": {
                "text": {
                    "statistical": {
                         "script": "doc['text'].values.size()"
                    }
                 }
             }
         }
	 * @return
	 * @throws IOException
	 */
    private static XContentBuilder getStatsTermsBuilder() throws IOException {
        XContentBuilder builder = XContentFactory.jsonBuilder();
        builder.startObject()
	    .startObject("query")
	    .startObject("match_all")
	    .endObject()
	    .endObject()
	    .startObject("facets")
	    .startObject("text")
	    .startObject("statistical")
	    .field("script", "doc['text'].values.size()")
	    .endObject()
	    .endObject()
	    .endObject()
	    .endObject();
        return builder;
    }

}