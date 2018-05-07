from xml.etree.ElementTree import XMLPullParser
from MongodbClient import MyMongoClient
import sys

client = MyMongoClient()
collection = client.get_collection('PostsPassFilters')
# list_of_keys = ['Id','Score','ViewCount','CommentCount']

PostsFilePath = './Data/Posts.xml'
startId = int(sys.argv[1]) if len(sys.argv) > 1 else 0
dbThreshold = int(sys.argv[2]) if len(sys.argv) > 2 else None
nextSwitchId = startId + dbThreshold if dbThreshold is not None else None
scoreThreshold = -2
viewThreshold = 100

parser = XMLPullParser(events=['end'])
with open(file=PostsFilePath) as f:
    Id = 0
    for line in f:
        parser.feed(line)
        for event,elem in parser.read_events():
            if elem.tag == 'row':
                Id = int(elem.get('Id'))
                if Id < startId:
                    continue
                score = int(elem.get('Score'))
                favoriteCount = int(elem.get('FavoriteCount'))
                postTypeId = int(elem.get('PostTypeId'))
                viewCount = int(elem.get('ViewCount'))
                if favoriteCount <= 0 and viewCount >= viewThreshold:
                    if postTypeId == 1:                    
                        answerCount = int(elem.get('AnswerCount'))
                    else:
                        answerCount = -1
                    commentCount = int(elem.get('CommentCount'))
                    if answerCount <= 0 and commentCount >= 0:
                        data_to_save = {}
                        data_to_save['Id'] = elem.get('Id')
                        data_to_save['Score'] = int(elem.get('Score'))
                        data_to_save['ViewCount'] = int(elem.get('ViewCount'))
                        data_to_save['CommentCount'] = int(elem.get('CommentCount'))
                        data_to_save['Body'] = elem.get('Body')
                        if postTypeId == 2: 
                            data_to_save['ParentId'] = elem.get('ParentId')
                        collection.insert_one(data_to_save)
        if nextSwitchId is not None and Id >= nextSwitchId:
            nextSwitchId += dbThreshold
            ret = client.switch_db()
            if ret:
                collection = client.get_collection('PostsPassFilters')
            else:
                break
    f.close()