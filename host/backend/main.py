from fastapi import FastAPI,File,UploadFile,Form,Body,Request
from typing import List
from bson import json_util
from bson.objectid import ObjectId
import uvicorn
from bardapi import Bard
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import uuid
from fastapi.encoders import jsonable_encoder
from bardapi import Bard
import PyPDF2
from pymongo import mongo_client
from motor.motor_asyncio import AsyncIOMotorClient
from PyPDF2 import PdfReader
from io import BytesIO
import pytesseract
import tempfile
from PIL import Image
from pdf2image.pdf2image import convert_from_bytes
import json
from datetime import date
from llama_index import (
    LLMPredictor,
    GPTVectorStoreIndex, 
    GPTListIndex, 
    GPTSimpleKeywordTableIndex,

)
from langchain.chat_models import ChatOpenAI
from llama_index.text_splitter import TokenTextSplitter
from llama_index import SimpleDirectoryReader, Document
from llama_index.node_parser import SimpleNodeParser
from llama_index.storage.docstore import MongoDocumentStore
import os
from llama_index.storage.docstore import MongoDocumentStore
from llama_index.storage.index_store import MongoIndexStore
from llama_index.storage.storage_context import StorageContext
from llama_index.storage.docstore import MongoDocumentStore
from llama_index import load_index_from_storage

# docstore = MongoDocumentStore.from_uri(uri="mongodb+srv://Hemanthgara:Hemanthg123@cluster0.bhsdppf.mongodb.net/?retryWrites=true&w=majority", db_name="file_storage")
# nodes = list(docstore.docs.values())

app=FastAPI()
#openai.api_key = ""  # Replace with your OpenAI API key
os.environ["OPENAI_API_KEY"] = "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"
#create client to mongodb and connection to the file_storage databases cluster and collection has connected files database
client=AsyncIOMotorClient("mongodb+srv://sivakumardogga1606:7gM0yvsoxzERiYOM@cluster0.bsqdr0j.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db=client["file_storage"]
collection=db["files"]
storage_context = StorageContext.from_defaults(
    docstore=MongoDocumentStore.from_uri(uri="mongodb+srv://sivakumardogga1606:7gM0yvsoxzERiYOM@cluster0.bsqdr0j.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", db_name="file_storage"),
    index_store=MongoIndexStore.from_uri(uri="mongodb+srv://sivakumardogga1606:7gM0yvsoxzERiYOM@cluster0.bsqdr0j.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", db_name="file_storage"),
)
origins=["http://localhost:4200"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)
@app.post('/get_record')
async def get_record(request:Request):
    data=await request.json()
    document_id = ObjectId(data["id"])
    cursor=await collection.find_one({"_id":document_id})
    record=json.loads(json_util.dumps(cursor))
    filenames=list(record["extractedText"].keys())
    options=[]
    for file in filenames:
        options.append({"label":file,"value":file})
    record["options"]=options
    return record
@app.get('/get_all_records')
async def get_all_records():
    cursor = collection.find()
    records = []
    async for record in cursor:
        record_dict = json.loads(json_util.dumps(record))
        records.append(record_dict)
    transformed_records=list(map(lambda record:{"id":record['_id']['$oid'],"title":record['title'],"date":record['date']},records))
    return {"data": transformed_records}
# @app.get('/delete')
# async def delete():
#     target_id = ObjectId("6479d0b7e7e1e7467ee0c6c3")
#     result = await collection.delete_many({"_id": {"$ne": target_id}})
#     return f"Deleted {result.deleted_count} records"
# @app.post('/getreply')
# async def get_reply(query: dict):
#    return {"message": query["query"]}

def extractText(contents:bytes)->str:
    pdf_file=BytesIO(contents)
        # with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_image:
        #     temp_image.write(pdf_file.getvalue())
        # text = pytesseract.image_to_string(Image.open(temp_image.name), lang="eng")
        # os.remove(temp_image.name)
    images = convert_from_bytes(pdf_file.read())
    # Perform OCR on the images
    text = ""
    i=0
    for image in images:
        text =text+"\n"+"below text is from page no "+str(i+1)+"\n"+pytesseract.image_to_string(image, lang="eng")
    
    return text

#main code to insert newly created chat
# the route that runs for upload
@app.post('/upload')
async def upload(title: str = Form(...), files: List[UploadFile] = File(...)):
    extractedText={}
    doc=[]
    for file in files:
        contents = await file.read()
        extractedText[file.filename]=extractText(contents)
        doc.append(Document(text=extractedText[file.filename]))
    nodes = SimpleNodeParser().get_nodes_from_documents(doc)
    docstore = MongoDocumentStore.from_uri(uri="mongodb+srv://Hemanthgara:Hemanthg123@cluster0.bhsdppf.mongodb.net/?retryWrites=true&w=majority")
    docstore.add_documents(nodes)
    list_index = GPTListIndex(nodes, storage_context=storage_context)
    vector_index = GPTVectorStoreIndex(nodes, storage_context=storage_context) 
    #keyword_table_index = GPTSimpleKeywordTableIndex(nodes, storage_context=storage_context) 
    docstore = MongoDocumentStore.from_uri(uri="mongodb+srv://Hemanthgara:Hemanthg123@cluster0.bhsdppf.mongodb.net/?retryWrites=true&w=majority", db_name="file_storage")
    nodes = list(docstore.docs.values())
    len(docstore.docs)
    result=await collection.insert_one({"title":title,"extractedText":extractedText,"date":str(date.today())})
    print("successfully inserted",str(result.inserted_id))
    return "success"


@app.post('/uploaded')
async def upload_file(file:UploadFile=File(...)):
    contents=await file.read()
    stored=await collection.find_one({"file_name":file.filename,"contents":contents})
    if(stored != None):
        print("hey we have uploaded and stored it")
        # stored_file=await collection.find_one({"file_name":file.filename,"contents":await file.read()})
        return {"extracted_text":stored["extracted_text"]}
        # pdf_file=BytesIO(file_contents)
        # with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_image:
        #     temp_image.write(pdf_file.getvalue())
        # text = pytesseract.image_to_string(Image.open(temp_image.name), lang="eng")
        # os.remove(temp_image.name)
        # images = convert_from_bytes(pdf_file.read())
        # Perform OCR on the images
        # text = ""
        # for image in images:
        #     text += pytesseract.image_to_string(image, lang="eng")
    else:
        # stored_file=await collection.find_one({"_id":result.inserted_id})
        # file_contents=stored_file["contents"]
        pdf_file=BytesIO(contents)
        # with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_image:
        #     temp_image.write(pdf_file.getvalue())
        # text = pytesseract.image_to_string(Image.open(temp_image.name), lang="eng")
        # os.remove(temp_image.name)
        images = convert_from_bytes(pdf_file.read())
        # Perform OCR on the images
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image, lang="eng")
        # text=pytesseract.image_to_string(pdf_file,lang="eng")
        # pdf_reader=PdfReader(pdf_file) # type: ignore
        # text=[pdf_reader.pages[page].extract_text() for page in range(len(pdf_reader.pages))]
        file_data={
                "file_name":file.filename,
                "contents":contents,
                "extracted_text":text,
                "chatHistory":[]
            }
        result=await collection.insert_one(file_data)
        print("successfully inserted",str(result.inserted_id))
        return {"extracted_text":text}
    
@app.post('/updateDetails')
async def updateDetails(title: str = Form(...), updateList:list=Form(...),files: List[UploadFile] = File(...)):
    return "green"

#main code to ask llm and get the response from it
@app.post('/getReponse')
async def getResponse(query:str = Form(...),ID:str =Form(...)):
    document_id = ObjectId(ID)
    cursor = await collection.find_one({"_id": document_id})
    record = json.loads(json_util.dumps(cursor))
    unique_id = str(uuid.uuid4())
    vector_index = load_index_from_storage(storage_context,index_id="09af8db0-e6a8-431e-a0a3-7b2543031d62")
    vector_response = vector_index.as_query_engine().query(query) 
    # display_response(vector_response)
    record['chatHistory'] = [{"message_id": unique_id, "Machine_response": str(vector_response), "Human_query": query}]
    del record['_id']
    chat_entry = {"message_id": unique_id, "Machine_response": str(vector_response), "Human_query": query}
    
    # Update the record in the collection to append to the chatHistory array
    result = await collection.update_one(
        {"_id": document_id},
        {"$push": {"chatHistory": chat_entry}}
    )
    # result = await collection.update_one({"_id": document_id}, {"$set": record})
    updated_record = await collection.find_one({"_id": document_id})
    updated_record_dict = json.loads(json_util.dumps(updated_record))
    return {"message": "success", "updated_record": updated_record_dict}

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
