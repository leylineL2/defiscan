import requests
import time
import json
import sys
import logging
from logging import getLogger, NullHandler, StreamHandler, INFO, DEBUG

logger = logging.getLogger(name=__name__)
logger.addHandler(NullHandler())

def main():
  address = sys.argv[1]
  logger.debug(f"address:{address}")
  num_transactions = 50
  last_id = 0
  f = open('transactions.txt', 'w')
  while num_transactions >= 50:
    time.sleep(5)
    response = requests.get(
        'https://api-binance-mainnet.cosmostation.io/v1/account/txs/%s' % address,
        params={'page': 1})
    logger.debug(f"response:{response}")
    transactions = response.json()
    transactions = eval(logs)
    print(f"transactions:{transactions}")
    num_transactions = transactions["txNums"]
    logger.debug(num_transactions)
    for transaction in transactions["txArray"]:
      last_id = transaction['blockHeight']
      logger.debug(last_id)
      f.write(json.dumps(transaction)+"\n")
      logger.debug(transaction)
  f.close()

if __name__== '__main__':
  root_logger = logging.getLogger()
  root_logger.addHandler(StreamHandler().setLevel(DEBUG))
  main()

