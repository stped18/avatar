import datetime
import json
import hashlib
import os
import random
import base64
import time

import flask
from flask import Flask, jsonify, send_from_directory, send_file


from apscheduler.schedulers.background import BackgroundScheduler
from models.avatar_generator import AvatarGenerator
import re

figurs = ["king", "gost", "flop"]

class Blockchain:
   def __init__(self):
       self.chain = []
       try:
            self.loadChain()
            print("loading chain")
       except:
           print("Creating new chain")
       if len(self.chain)<=0:
            image_file_names = os.listdir("./models/images/")
            generator = AvatarGenerator("./models/images/" + image_file_names[random.randint(0, 2)])
            block = self.create_blockchain(proof=140040470400, previous_hash='8c57874897712e9b732e0ae80b7d369da3b6f6784ec15d2b6ef75ddfa15b5fa9')
            raraty, dimons , season, amount= generator.generate_avatar(block['index'], block['timestamp'], block['proof'],
                                                  block['previous_hash'])
            self.get_previous_block()["rarity"] = raraty
            self.get_previous_block()["dimons"] = dimons
            self.get_previous_block()["season"] = season
            self.write_json(self.chain)


   def write_json(self,chain, filename='./models/chain.json'):
       with open(filename, 'w') as outfile:
           json.dump(chain, outfile, indent=4)
   def loadChain(self, filename='./models/chain.json'):
       with open(filename) as json_file:
           self.chain = json.load(json_file)




   def create_blockchain(self, proof, previous_hash):
       block = {
           'index': len(self.chain) + 1,
           'timestamp': str(datetime.datetime.now()),
           'proof': proof,
           'previous_hash': previous_hash,
           'rarity':0,
           'dimons':0,
           'season':"None",
       }
       self.chain.append(block)
       return block

   def get_previous_block(self):
       last_block = self.chain[-1]
       return last_block

   def proof_of_work(self, previous_proof):
       # miners proof submitted
       new_proof = 1
       # status of proof of work
       check_proof = False
       while check_proof is False:
           # problem and algorithm based off the previous proof and new proof
           hash_operation = hashlib.sha256(str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
           # check miners solution to problem, by using miners proof in cryptographic encryption
           # if miners proof results in 4 leading zero's in the hash operation, then:
           if hash_operation[:4] == '0000':
               check_proof = True
           else:
               # if miners solution is wrong, give mine another chance until correct
               new_proof += 1
       return new_proof

   # generate a hash of an entire block
   def hash(self, block):
       encoded_block = json.dumps(block, sort_keys=True).encode()
       return hashlib.sha256(encoded_block).hexdigest()

   # check if the blockchain is valid
   def is_chain_valid(self, chain):
       # get the first block in the chain and it serves as the previous block
       previous_block = chain[0]
       # an index of the blocks in the chain for iteration
       block_index = 1
       while block_index < len(chain):
           # get the current block
           block = chain[block_index]
           # check if the current block link to previous block has is the same as the hash of the previous block
           if block["previous_hash"] != self.hash(previous_block):
               return False
           # get the previous proof from the previous block
           previous_proof = previous_block['proof']
           # get the current proof from the current block
           current_proof = block['proof']
           # run the proof data through the algorithm
           hash_operation = hashlib.sha256(str(current_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
           # check if hash operation is invalid
           if hash_operation[:4] != '0000':
               return False
           # set the previous block to the current block after running validation on current block
           previous_block = block
           block_index += 1
       return True


PEOPLE_FOLDER = os.path.join('static', 'images')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER

blockchain = Blockchain()

@app.route('/get_last-block')
def getLastBlock ():
    block=blockchain.get_previous_block()
    response = {'message': 'last block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'rarity': block['rarity'],
                'dimons': block['dimons'],
                'season': block['season']}
    return jsonify(response), 200



@app.route('/download/<hash>')
def downloadFile (hash):

    fullpath = "templates/static/images/" + hash + ".png"
    print(fullpath)
    return send_file(fullpath, as_attachment=True)

@app.route("/imgs/<hash>")
def images(hash):
    fullpath = "templates/static/images/" + hash +".png"
    print(fullpath)
    resp = flask.make_response(flask)
    resp.content_type = "image/png"
    return resp
@app.route('/mine_block', methods=['GET'])
def mine_block():
    # get the data we need to create a block
    blockchain.is_chain_valid(blockchain.chain)
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_blockchain(proof, previous_hash)
    image_file_names = os.listdir("./models/images/")
    generator = AvatarGenerator("./models/images/" + image_file_names[random.randint(0, 2)])
    raraty, dimons, season, amount = generator.generate_avatar(block['index'] , block['timestamp'], block['proof'], block['previous_hash'])
    blockchain.get_previous_block()["rarity"]=raraty
    blockchain.get_previous_block()["dimons"]=dimons
    blockchain.get_previous_block()["season"] = season
    write_json(blockchain.chain)
    response = {'message': 'Block mined!',
               'index': block['index'],
               'timestamp': block['timestamp'],
               'proof': block['proof'],
               'previous_hash': block['previous_hash'],
               'rarity':block['rarity'],
               'dimons':block['dimons'],
               'season':block['season']}
    return jsonify(response), 200


def write_json( chain, filename='models/chain.json'):
    with open(filename, 'w') as outfile:
        json.dump(chain, outfile,indent=4)

@app.route('/get_chain', methods=['GET'])
def get_chain():
   response = {'chain': blockchain.chain,
               'length': len(blockchain.chain)}
   return jsonify(response), 200


if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5000)

