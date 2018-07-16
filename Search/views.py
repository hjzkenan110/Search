import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View
from datetime import datetime
from elasticsearch import Elasticsearch
client = Elasticsearch()

# Create your views here.
class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get("s", "")
        re_datas = []
        if key_words:
            re_datas = get_suggest(key_words)
        return HttpResponse(json.dumps(re_datas), content_type="application/json")


def get_suggest(word):

    ls = []
    r = client.search(             
        index="appdata",       
        body={                 
            "suggest":{              
                "my-suggest":{         
                    "text": word,  
                    "completion": {      
                        "field":"suggest", 
                        "fuzzy":{ "fuzziness":2 } 
                    }                    
                }                      
            },                       
            "_source": "appName"     
        }                          
    )                          

    for i in r['suggest']['my-suggest']:
        a = i['options'][0]['_source']['appName']
        ls.append(a)
        
    pass
    return ls


class SearchView(View):
    def get(self, request):
        key_words = request.GET.get("q","")

        page = request.GET.get("p", "1")
        try:
            page = int(page)
        except:
            page = 1

        #jobbole_count = redis_cli.get("jobbole_count")
        start_time = datetime.now()
        response = client.search(
            index= "appdata",
            body={
                "query":{
                    "multi_match":{
                        "query":key_words,
                        "fields":["appID", "appName"]
                    }
                },
                "from":(1-1)*10,
                "size":10,
                "highlight": {
                    "pre_tags": ['<span class="keyWord">'],
                    "post_tags": ['</span>'],
                    "fields": {
                        "appID": {},
                        "appName": {},
                    }
                }
            }
        )
                
        end_time = datetime.now()
        last_seconds = (end_time-start_time).total_seconds()
        total_nums = response["hits"]["total"]
        if (page%10) > 0:
            page_nums = int(total_nums/10) +1
        else:
            page_nums = int(total_nums/10)
        hit_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            if "appId" in hit["highlight"]:
                hit_dict["appId"] = "".join(hit["highlight"]["appId"])
            else:
                hit_dict["appId"] = hit["_source"]["appId"]
            if "appName" in hit["highlight"]:
                hit_dict["appName"] = "".join(hit["highlight"]["appName"])
            else:
                hit_dict["appName"] = hit["_source"]["appName"]

            hit_dict["create_date"] = hit["_source"]["create_date"]
            hit_dict["url"] = hit["_source"]["url"]
            hit_dict["score"] = hit["_score"]

            hit_list.append(hit_dict)

            return render(request, "result.html", {"page":page,
                                                    "all_hits":hit_list,
                                                    "key_words":key_words,
                                                    "total_nums":total_nums,
                                                    "page_nums":page_nums,
                                                    "last_seconds":last_seconds})
