from pymongo import MongoClient, results
import configparser
import time

config = configparser.ConfigParser()
config.read('config.cfg')


class Mongo:
    client = MongoClient(config['MONGODB']['CONNECTION_STRING'])
    db = client[config['MONGODB']['DATABASE']]
    collection = db[config['MONGODB']['COLLECTION']]

    def __init__(self) -> None:
        pass

    def news_insert(self, news) -> results.InsertOneResult:
        """
        Insert news to MongoDB

        Args:
            news (Dict): Dictionary containing key-value pairs

        Return:
            InsertOneResult (Dict):
                acknowledged (bool): True of False depending on the success of insertion
                inserted_id (Any): _id of inserted news
        """
        news['_id'] = news['oid'] + news['aid']
        news['insertTime'] = time.strftime('%Y-%m-%d %H:%M:%S')
        # news['insertTime'] = datetime.now()
        return self.collection.insert_one(news)

    def news_find(self, id):
        pass

    def news_delete(self, id) -> results.DeleteResult:
        """
        Delete news from MongoDB

        Args:
            id (str): _id value of news object

        Return:
            DeleteResult (Dict):
                acknowledged (bool): True of False depending on the success of deletion
                deleted_count (int): Number of documents deleted
        """
        return self.collection.delete_one(
            {'_id': id}
        )


if __name__ == "__main__":

    mongo = Mongo()

    news = {
        'oid': "123",
        'aid': "456789"
    }

    print(mongo.news_delete("123456789").deleted_count)
    # mongo.news_insert(news)
