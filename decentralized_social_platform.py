from web3 import Web3

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

class User:
    def __init__(self, username, private_key):
        self.username = username
        self.private_key = private_key
        self.data = []

contract_source_code = """
pragma solidity ^0.8.0;

contract DecentralizedSocialPlatform {
    struct Post {
        address user;
        string content;
    }

    mapping(uint256 => Post) public posts;
    uint256 public postCount;

    function createPost(string memory _content) public {
        postCount++;
        posts[postCount] = Post(msg.sender, _content);
    }
}
"""

def deploy_contract():
    if not w3.isConnected():
        print("Ethereum node not connected.")
        return None

    account = w3.eth.account.create()
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = contract.constructor().transact({'from': account.address, 'gas': 1000000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    return contract, account


compiled_contract = w3.eth.compile_source(contract_source_code)
abi = compiled_contract['<stdin>:DecentralizedSocialPlatform']['abi']
bytecode = compiled_contract['<stdin>:DecentralizedSocialPlatform']['evm']['bytecode']['object']

social_contract, deployer_account = deploy_contract()

alice = User("Alice", Web3.toHex(Web3.sha3(text="password_alice")))
bob = User("Bob", Web3.toHex(Web3.sha3(text="password_bob")))


def create_post(user, content):
    transaction = social_contract.functions.createPost(content).buildTransaction({
        'from': user.address,
        'gas': 1000000,
        'gasPrice': w3.toWei('40', 'gwei'),
        'nonce': w3.eth.getTransactionCount(user.address),
    })

    signed_transaction = w3.eth.account.sign_transaction(transaction, user.private_key)
    tx_hash = w3.eth.sendRawTransaction(signed_transaction.rawTransaction)
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

create_post(alice, "Excited to join the decentralized platform!")
create_post(bob, "Exploring the new social network")

def get_posts():
    posts = []
    for i in range(1, social_contract.functions.postCount().call() + 1):
        post = social_contract.functions.posts(i).call()
        posts.append({'user': post[0], 'content': post[1]})
    return posts

posts = get_posts()
for post in posts:
    print(f"User: {post['user']}, Content: {post['content']}")
