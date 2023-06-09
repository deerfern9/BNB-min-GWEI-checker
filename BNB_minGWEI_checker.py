from web3 import Web3
from web3.middleware import geth_poa_middleware
import requests
import time
import telebot

##############################################
tg_channel = '@some_channel'
api_tg = 'tg bot api'
bscscan_api = 'bscscan api'
last_block_number = 27605552
##############################################

validators = {'Legend III': '0x8b6C8fd93d6F4CeA42Bbb345DBc6F0DFdb5bEc73', 'Legend I': '0x295e26495cef6f69dfa69911d9d8e4f3bbadb89b'}     # '0x35EBb5849518aFF370cA25E19e1072cC1a9FAbCa': '0x35EBb5849518aFF370cA25E19e1072cC1a9FAbCa',
w3 = Web3(Web3.HTTPProvider('https://bsc.blockpi.network/v1/rpc/public'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
bot = telebot.TeleBot(api_tg)
same_block_count = 0
i = 0


def start_message():
    global i
    global last_block_number
    global same_block_count
    while True:
        try:
            response = requests.post(
                f'https://api.bscscan.com/api?module=account&action=txlist&address={list(validators.values())[i]}&startblock=0&endblock=99999999&page=1&offset=10&sort=desc&apikey={bscscan_api}').json()
        except Exception as e:
            print(e)
            time.sleep(5)
            continue
        try:
            block_number = int(response['result'][0]['blockNumber'])
        except Exception as e:
            print(e)
            time.sleep(5)
            continue
        if block_number <= last_block_number:
            print(response)
            print(f'same block {block_number}')
            same_block_count += 1
            if same_block_count >= 15:
                i += 1
                same_block_count = 0
                if i > len(validators)-1:
                    i = 0
            time.sleep(5)
            continue
        try:
            block = w3.eth.getBlock(block_number, full_transactions=False)
        except Exception as e:
            print(e)
            time.sleep(20)
            continue
        transaction_hashes = block['transactions']

        all_gwei = []

        print(f"Transaction hashes in block {block_number}:")
        for tx_hash in transaction_hashes[-10:]:
            transaction_hash = tx_hash.hex()
            try:
                transaction = w3.eth.getTransaction(transaction_hash)
            except Exception as e:
                print(e)
                continue

            print("Transaction information:")
            print(f"  Hash: {transaction_hash}")
            print(f"  Gas linit: {transaction['gas']}")
            print(f"  GWEI: {Web3.fromWei(transaction['gasPrice'], 'gwei')} gwei")
            all_gwei.append(Web3.fromWei(transaction['gasPrice'], 'gwei'))
        while 0 in all_gwei:
            all_gwei.remove(0)
        print(f'\nMinimum GWEI: {min(all_gwei)}')
        try:
            bot.send_message(tg_channel, f'👼 Validator: {list(validators.keys())[i]}\n💠 Block: {block_number}\n🔥 Minimum GWEI: {min(all_gwei)}')
        except Exception as e:
            print(e)
            continue
        if min(all_gwei[:-1]) >= 3:
            i += 1
            if i > len(validators)-1:
                i = 0
        last_block_number = block_number
        time.sleep(5)


if __name__ == '__main__':
    start_message()
    bot.polling()
