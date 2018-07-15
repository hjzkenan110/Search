from django.db import models
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, Completion, Keyword, Text, Integer, Double

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["localhost"])

class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])

class QimaiType(DocType):
    suggest = Completion(analyzer=ik_analyzer)
    appId = Keyword()
    appName = Text(analyzer="ik_max_word")
    icon = Keyword()
    publisher = Text(analyzer="ik_max_word")
    country = Text(analyzer="ik_max_word")
    genre = Text(analyzer="ik_max_word")
    price = Double()
    releaseTime = Date()

    class Meta:
        index = "appdata"
        doc_type = "appinfo"


if __name__ == "__main__":
    QimaiType.init()
