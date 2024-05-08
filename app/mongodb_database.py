import pymongo
import yaml
from path import directory
from pprint import pprint
from bson import ObjectId
import bson

CONFIGFILE = 'config.yaml'

class MongoDataBase():
    def __init__(self) -> None:
        self.client = pymongo.MongoClient("mongodb+srv://denikryt:D3778228545dan@cluster0.7qzx9lz.mongodb.net/")
        self.db = self.client['Users']
    
    def add_new_user(self, data):
        user_id = str(data.get('user_id'))

        if not self.is_user_collection_exists(user_id):
            self.db.create_collection(user_id)

            collection = self.db[user_id]

            document = {'info': {'user_id':data.get('user_id'),
                                'user_name':data.get('user_name'),
                                'channel_id':0,
                                'last_message_id':data.get('message_id'),
                                'languages': []}}
            
            result = collection.insert_one(document)
            print(f"New user was added! User_id: {user_id}. Inserted id: {result.inserted_id}")
            return True
        else:
            print(f"Collection for user {user_id} is already exists!")
            return False
    
    def add_new_language(self, user_id, language):
        document = {'list_words':[],
                    'texts':[],
                    'words':[] }
        try:
            collection = self.db[str(user_id)]
            result = collection.update_one({},
                {'$set': {language: document}},
                upsert=True)
            
            print(f"Language added for user_id {user_id}. Matched {result.matched_count} document(s) and modified {result.modified_count} document(s).")
        except pymongo.errors.PyMongoError as e:
            print(f"Error adding language for user_id {user_id}: {e}")

    def add_language_to_info(self, user_id, language):
        try:
            collection = self.db[str(user_id)]
            result = collection.update_one({}, {'$push': {'info.languages': language}})
            
            print(f"Language added to info.languages for user_id {user_id}. Matched {result.matched_count} document(s) and modified {result.modified_count} document(s).")
        except pymongo.errors.PyMongoError as e:
            print(f"Error adding language to info.languages for user_id {user_id}: {e}")

    def add_new_text(self, user_id, language, textData):
        if not self.is_user_collection_exists(user_id):
            print('User does not exist!')
            return None

        if not self.is_language_exists(user_id, language):
            self.add_new_language(user_id, language)
            self.add_language_to_info(user_id, language)

        document = {
                    'text':textData.get('text'),
                    'text_id':ObjectId(),
                    'words':[]
                }
        try:
            collection = self.db[str(user_id)]
            result = collection.update_one({}, {'$push': {f'{language}.texts': document}})
            
            print(f"Text added to {language} for user_id {user_id}. Matched {result.matched_count} document(s) and modified {result.modified_count} document(s).")
            return True
        except pymongo.errors.PyMongoError as e:
            print(f"Error adding text to {language} for user_id {user_id}: {e}")
            return False

    def add_word_to_list_words(self, collection, language, form):
        try:
            result = collection.update_one({}, {'$push': {f'{language}.list_words': form.get('word')}})
            
            print(f"Word {form.get('word')} added to {language}.list_words.")
            return True
        
        except pymongo.errors.PyMongoError as e:
            print(f"Error adding word {form.get('word')} to {language}.list_words: {e}")
            raise e

    def add_word_object(self, collection, language, form):
        try:
            word_document = {
                "word": form.get("word"),
                "text_source": [{'text_id' : form.get("text_id"), 
                             'sent_id' : form.get("sent_id")}],
                "word_id": ObjectId(),
                "mark": 0,
                "translation": [x for x in form.get("translation")],
            }
            result = collection.update_one({}, {'$push': {f'{language}.words': word_document}})
            
            print(f"Word {form.get('word')} document added to {language}.words.")
            return True
        
        except pymongo.errors.PyMongoError as e:
            print(f"Error adding word {form.get('word')} document to {language}.words: {e}")
            raise e
    
    def add_word_to_text_object(self, collection, language, form):

        word_objcect = {
            "word": form.get("word"),
            "translation_id" : 0 }

        try:
            result = collection.update_one({f'{language}.texts': {'$elemMatch': {'text_id': form.get("text_id")}}},
                                           {'$push': {f'{language}.texts.$.words': word_objcect}})
            
            print(f"Word {form.get('word')} added to {language}.texts.words for text_id {form.get('text_id')}.")
            return True
        
        except pymongo.errors.PyMongoError as e:
            print(f"Error adding word {form.get('word')} to {language}.texts.words for text_id {form.get('text_id')}: {e}")
            raise e

    def add_new_word(self, user_id, language, form):
        collection = self.db[str(user_id)]
        user_document = collection.find_one({})

        if user_document:
            try:
                if self.validate_word_form(form) and self.is_text_exists(user_document, language, form.get("text_id")):
                
                    self.add_word_to_list_words(collection, language, form)
                    self.add_word_object(collection, language, form)
                    self.add_word_to_text_object(collection, language, form)

                    print("Word added successfully.")
                    return True
                
            except Exception as e: 
                print(f"Error adding word: {e}")
                return False
        else:
            print(f"User {user_id} does not exist.")
            return False

    def add_translation_to_word(self, user_id, language, text_id, translation, db_name, collection_name):
        db = self.client[db_name]
        collection = db[collection_name]

        # Find the user document by user_id
        user_document = collection.find_one({"info.user_id": user_id})

        if user_document:
            # Find the language within the user's languages list
            for lang in user_document.get("languages", []):
                if language in lang:
                    # Find the word with the specified text_id
                    for word in lang[language].get("words", []):
                        if word.get("text_id") == text_id:
                            # Add translation to the word's translation field
                            word["translation"].append(translation)

                            # Update the user document in the collection
                            collection.update_one({"info.user_id": user_id}, {"$set": user_document})

                            print("Translation added successfully.")
                            return True
    
    
    def update_last_message_id(self, user_id, message_id):
        try:
            collection = self.db[str(user_id)]
            result = collection.update_one({}, {'$set': {'info.last_message_id': message_id}})
            
            print(f"Last_message_id {message_id} updated for user_id {user_id}.")
        except pymongo.errors.PyMongoError as e:
            print(f"Error updating last_message_id for user_id {user_id}: {e}")

    def get_last_message_id(self, user_id):
        try:
            collection = self.db[str(user_id)]
            document = collection.find_one({})
            return document['info']['last_message_id']
        except pymongo.errors.PyMongoError as e:
            print(f"Error getting last_message_id for user_id {user_id}: {e}")
            return None

    def get_list_words(self, user_id, language):
        try:
            collection = self.db[str(user_id)]
            document = collection.find_one({})
            if document and language in document:
                return document[language]['list_words']
            else:
                return []
        except pymongo.errors.PyMongoError as e:
            print(f"Error getting {language}.list_words for user_id {user_id}: {e}")
            return []
    
    def get_text_by_text_id(self, user_id, language, text_id):
        collection = self.db[str(user_id)]

        user_document = collection.find_one({})
        if user_document:
            for textObject in user_document[language].get("texts", []):
                if textObject.get("text_id") == text_id:
                    return textObject.get("text")
        
    def get_all_texts(self, user_id, language):
        collection = self.db[str(user_id)]

        user_document = collection.find_one({})
        if user_document:
            return [textObject for textObject in user_document[language].get("texts", [])]

    def get_all_word_objects(self, user_id, language):
        collection = self.db[str(user_id)]

        user_document = collection.find_one({})
        if user_document:
            return user_document[language].get("words", [])


    def validate_word_form(self, form):
        try:
            word = form.get("word")
            text_id = form.get("text_id")
            sent_id = form.get("sent_id")
            translation = form.get("translation")

            # Validate required fields
            if word is None or word == "":
                raise ValueError("Word is required.")
            
            if text_id is None or text_id == "":
                raise ValueError("Text_id is required.")
            
            if sent_id is None or sent_id == "":
                raise ValueError("Sent_id is required.")
            
            if translation is None or translation == "":
                raise ValueError("Translation is required.")
            

            # Validate types
            if not isinstance(word, str):
                raise ValueError("Word must be a string.")

            if not isinstance(text_id, bson.objectid.ObjectId):
                raise ValueError("Text_id must be an integer.")

            if not isinstance(sent_id, int):
                raise ValueError("Sent_id must be an integer.")

            if not isinstance(translation, list):
                raise ValueError("Translation must be a list.")

            # Additional type validations for translation elements
            for element in translation:
                if not isinstance(element, str):
                    raise ValueError("Each element in the translation list must be a string.")

            return True
        
        except ValueError as ve:
            print(f"Validation error: {ve}")
            return False

    def is_text_exists(self, user_document, language, text_id):
        try:
            text_ids = []
            for text in user_document[language].get("texts", []):
                text_ids.append(text.get("text_id"))
                if text.get("text_id") == text_id:
                    return True
            
            print(f"Text with text_id {text_id} does not exist")
            print(f"Existing text_ids: {text_ids}")
            return False        
            
        except pymongo.errors.PyMongoError as e:
            print(f"Error checking text existence: {e}")
            return False

    def is_word_in_list_words(self, user_id, language, word_to_check):
        try:
            collection = self.db[str(user_id)]
            document = collection.find_one({})
            return word_to_check in document[language]['list_words']

        except pymongo.errors.PyMongoError as e:
            print(f"Error checking word existence in {language}.list_words: {e}")
            return False

    def is_language_exists(self, user_id, language):
        try:
            collection = self.db[str(user_id)]
            document = collection.find_one({})
            if document and language in document:
                return True
            else:
                return False
        except pymongo.errors.PyMongoError as e:
            print(f"Error checking language existence for user_id {user_id}: {e}")
            return False
        
    def is_user_collection_exists(self, user_id):
        return str(user_id) in self.db.list_collection_names()


    def delete_all_words(self, user_id, language):
        collection = self.db[str(user_id)]
        user_document = collection.find_one({})

        if user_document:
            for text_object in user_document[language].get("texts", []):
                text_object["words"] = []

            collection.update_one({}, {'$set': {f'{language}.texts': user_document[language].get("texts", [])}})
            collection.update_one({}, {'$set': {f'{language}.list_words': []}})
            collection.update_one({}, {'$set': {f'{language}.words': []}})
            
            print('All words were deleted successfully!')
            return True
        else:
            print(f'User {user_id} not found!')
            return False

    def delete_word(self, user_id, language, word):
        collection = self.db[str(user_id)]
        user_document = collection.find_one({})
        
        if user_document:

            for word_object in user_document[language].get("words", []):
                if word_object.get("word") == word:
                    text_source_list = word_object.get("text_source")
                    break

            text_source_ids = [text_source_object.get("text_id") for text_source_object in text_source_list]

            # Delete word from list_words
            collection.update_one({}, {'$pull': {f'{language}.list_words': word}})

            #delete word object from {language}.wordsmessage, call
            collection.update_one({}, {'$pull': {f'{language}.words': {'word': word}}})

            #get text object from {language}.texts by text_id
            text_objects = user_document[language].get("texts", [])

            for text_obj in text_objects:
                if text_obj.get("text_id") in text_source_ids:
                    text_obj_words = text_obj.get("words")
                    for word_obj in text_obj_words:
                        if word_obj.get("word") == word:
                            text_obj_words.remove(word_obj)
            
            collection.update_one({}, {'$set': {f'{language}.texts': text_objects}})
            
            print(f"Word {word} deleted successfully.")
            return True
        else:
            print(f"User {user_id} does not exist.")
            return False

    def delete_user(self, user_id):
        self.db.drop_collection(str(user_id))

    def delete_texts_by_language(self, user_id, language):
        try:
            collection = self.db[str(user_id)]
            result = collection.update_one({}, {'$set': {f'{language}.texts': []}})
            
            print(f"All texts deleted for user_id {user_id}, language {language}. Matched {result.matched_count} document(s) and modified {result.modified_count} document(s).")
        except pymongo.errors.PyMongoError as e:
            print(f"Error deleting all texts for user_id {user_id}, language {language}: {e}")

    def delete_text_by_id(self, user_id, language, text_id):
        try:
            collection = self.db[str(user_id)]
            result = collection.update_one({f'{language}.texts.text_id': text_id},
                                           {'$pull': {f'{language}.texts': {'text_id': text_id}}})
            
            print(f"Text deleted for user_id {user_id}, language {language}, text_id {text_id}. Matched {result.matched_count} document(s) and modified {result.modified_count} document(s).")
        except pymongo.errors.PyMongoError as e:
            print(f"Error deleting text for user_id {user_id}, language {language}, text_id {text_id}: {e}")

    def delete_all_word_objects(self, user_id, language):
        try:
            collection = self.db[str(user_id)]
            result = collection.update_one({}, {'$set': {f'{language}.words': []}})
            
            print(f"All word documents deleted for user_id {user_id}, language {language}. Matched {result.matched_count} document(s) and modified {result.modified_count} document(s).")
        except pymongo.errors.PyMongoError as e:
            print(f"Error deleting all word documents for user_id {user_id}, language {language}: {e}")

    def delete_all_collections(self):
        user_collections = self.db.list_collection_names()
        for user_collection_name in user_collections:
            self.db.drop_collection(user_collection_name)
            print(f"Collection {user_collection_name} deleted.")

    def delete_all_texts(self, user_id, language):
        try:
            collection = self.db[str(user_id)]
            result = collection.update_one({}, {'$set': {f'{language}.texts': []}})
            
            print(f"All texts deleted for user_id {user_id}, language {language}.")
        except pymongo.errors.PyMongoError as e:
            print(f"Error deleting all texts for user_id {user_id}, language {language}: {e}")

    def print_user_document(self, user_id):
        collection = self.db[str(user_id)]
        for user_document in collection.find():
                pprint(user_document)
                print("\n")

    def print_all_documents(self):
        user_collections = self.db.list_collection_names()

        for user_collection_name in user_collections:
            user_collection = self.db[user_collection_name]
            print(f"Documents in Users.{user_collection_name}:")
            for user_document in user_collection.find():
                pprint(user_document)
                print("\n")