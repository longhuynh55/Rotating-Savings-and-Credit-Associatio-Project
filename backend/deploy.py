import json
import os
from web3 import Web3
from solcx import compile_standard, install_solc
import streamlit as st

def deploy_contract(max_members=5, contribution_amount=1, private_key=None):
    """Triển khai smart contract ChoiHui lên Ganache"""
    # Cài đặt solc nếu chưa có
    try:
        install_solc("0.8.0")
    except:
        print("Đã cài đặt solc, tiếp tục...")
    
    # Thiết lập kết nối web3
    ganache_url = "http://127.0.0.1:7545"
    w3 = Web3(Web3.HTTPProvider(ganache_url))
    
    if not w3.is_connected():
        return None, "Không thể kết nối đến Ganache. Vui lòng đảm bảo Ganache đã chạy."
    
    # Lấy tài khoản
    accounts = w3.eth.accounts
    if not accounts:
        return None, "Không tìm thấy tài khoản nào trong Ganache."
    
    admin_account = accounts[0]
    
    # Đọc file contract
    with open("contracts/ChoiHui.sol", "r", encoding="utf-8") as file:
        contract_source = file.read()
    
    # Biên dịch Solidity
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"ChoiHui.sol": {"content": contract_source}},
            "settings": {
                "outputSelection": {
                    "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                }
            },
        },
        solc_version="0.8.0",
    )
    
    # Lấy dữ liệu contract
    contract_data = compiled_sol["contracts"]["ChoiHui.sol"]["ChoiHui"]
    contract_bytecode = contract_data["evm"]["bytecode"]["object"]
    contract_abi = contract_data["abi"]
    
    # Lưu ABI vào file
    os.makedirs("backend/data", exist_ok=True)
    with open("backend/data/contract_abi.json", "w") as file:
        json.dump(contract_abi, file)
    
    # Tạo contract
    Contract = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
    
    # Lấy transaction count
    nonce = w3.eth.get_transaction_count(admin_account)
    
    # Xây dựng, ký và gửi transaction
    transaction = Contract.constructor(max_members, contribution_amount).build_transaction(
        {
            "chainId": w3.eth.chain_id,
            "from": admin_account,
            "nonce": nonce,
            "gasPrice": w3.eth.gas_price,
        }
    )
    
    if not private_key:
        # Sử dụng private key mặc định của Ganache nếu không có private key được cung cấp
        private_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"  # Ganache default
    
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
    
    # Gửi transaction
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    # Đợi transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = tx_receipt.contractAddress
    
    # Lưu địa chỉ contract vào file
    with open("backend/data/contract_address.txt", "w") as file:
        file.write(contract_address)
    
    return contract_address, f"Contract được triển khai tại địa chỉ: {contract_address}"

if __name__ == "__main__":
    contract_address, message = deploy_contract()
    if contract_address:
        print(message)
    else:
        print(f"Lỗi: {message}")