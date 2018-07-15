import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View

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


if __name__ == "__main__":
    get_suggest("fighting")