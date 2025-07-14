import json
import os
from web3 import Web3

class ChoiHuiContract:
    def __init__(self, ganache_url="http://127.0.0.1:7545"):
        # Kết nối tới Ganache
        self.w3 = Web3(Web3.HTTPProvider(ganache_url))
        
        if not self.w3.is_connected():
            raise Exception("Không thể kết nối đến Ganache. Vui lòng kiểm tra Ganache đã chạy chưa.")
        
        # Lấy địa chỉ contract và ABI
        try:
            with open("backend/data/contract_address.txt", "r") as file:
                self.contract_address = file.read().strip()
            
            with open("backend/data/contract_abi.json", "r") as file:
                self.contract_abi = json.load(file)
        except FileNotFoundError:
            raise Exception("Contract chưa được triển khai. Hãy chạy deploy.py trước.")
        
        # Tạo instance của contract
        self.contract = self.w3.eth.contract(
            address=self.contract_address, abi=self.contract_abi
        )
    
    def get_accounts(self):
        """Lấy danh sách các tài khoản từ Ganache"""
        return self.w3.eth.accounts
    
    def get_contract_info(self):
        """Lấy thông tin cơ bản của contract"""
        chu_hui = self.contract.functions.chuHui().call()
        so_thanh_vien_toi_da = self.contract.functions.soThanhVienToiDa().call()
        tien_mot_ky = self.contract.functions.tienMotKy().call()
        tien_ky_quy = self.contract.functions.tienKyQuyToiThieu().call()
        ky_hien_tai = self.contract.functions.kyHienTai().call()
        tong_so_ky = self.contract.functions.tongSoKy().call()
        
        return {
            "chu_hui": chu_hui,
            "so_thanh_vien_toi_da": so_thanh_vien_toi_da,
            "tien_mot_ky": self.w3.from_wei(tien_mot_ky, "ether"),
            "tien_ky_quy": self.w3.from_wei(tien_ky_quy, "ether"),
            "ky_hien_tai": ky_hien_tai,
            "tong_so_ky": tong_so_ky
        }
    
    def get_member_list(self):
        """Lấy danh sách thành viên"""
        members = []
        try:
            i = 0
            while True:
                member = self.contract.functions.danhSachNguoiChoi(i).call()
                member_info = self.contract.functions.danhSachHuiVien(member).call()
                members.append({
                    "dia_chi": member,
                    "da_hut_hui": member_info[2],  # daHutHui
                    "so_tien_keu_hui": self.w3.from_wei(member_info[3], "ether"),  # soTienKeuHui
                    "da_dong_tien_hui": member_info[4],  # daDongTienHui
                    "la_hui_chet": member_info[5],  # laHuiChet
                    "tien_ky_quy": self.w3.from_wei(member_info[6], "ether")  # soTienKyQuy
                })
                i += 1
        except:
            # Không còn thành viên nào
            pass
        
        return members
    
    def get_current_recipient(self):
        """Lấy người nhận hụi hiện tại"""
        try:
            recipient = self.contract.functions.nguoiNhanHui().call()
            if recipient == "0x0000000000000000000000000000000000000000":
                return None
            return recipient
        except:
            return None
    
    def join_hui(self, account, private_key):
        """Tham gia hụi bằng cách đặt cọc"""
        deposit_amount = self.contract.functions.tienKyQuyToiThieu().call()
        
        transaction = self.contract.functions.thamGiaHui().build_transaction({
            "chainId": self.w3.eth.chain_id,
            "from": account,
            "value": deposit_amount,
            "nonce": self.w3.eth.get_transaction_count(account),
            "gasPrice": self.w3.eth.gas_price
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)
    
    def bid_for_hui(self, account, private_key, bid_amount):
        """Kêu hụi (đấu thầu) để nhận quỹ"""
        transaction = self.contract.functions.keuHui(int(bid_amount)).build_transaction({
            "chainId": self.w3.eth.chain_id,
            "from": account,
            "nonce": self.w3.eth.get_transaction_count(account),
            "gasPrice": self.w3.eth.gas_price
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)
    
    def select_recipient(self, admin_account, private_key):
        """Chủ hụi chọn người nhận hụi cho kỳ hiện tại"""
        transaction = self.contract.functions.chonNguoiNhanHui().build_transaction({
            "chainId": self.w3.eth.chain_id,
            "from": admin_account,
            "nonce": self.w3.eth.get_transaction_count(admin_account),
            "gasPrice": self.w3.eth.gas_price
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)
    
    def contribute(self, account, private_key):
        """Đóng tiền hụi cho kỳ hiện tại"""
        # Lấy người nhận hụi
        recipient = self.contract.functions.nguoiNhanHui().call()
        
        # Lấy thông tin thành viên
        member_info = self.contract.functions.danhSachHuiVien(account).call()
        
        # Tính số tiền cần đóng
        base_amount = self.contract.functions.tienMotKy().call()
        bid_amount = self.contract.functions.danhSachHuiVien(recipient).call()[3]  # soTienKeuHui
        
        contribution_amount = base_amount
        if not member_info[5]:  # if not laHuiChet
            contribution_amount = base_amount - bid_amount
        
        transaction = self.contract.functions.dongTienHui().build_transaction({
            "chainId": self.w3.eth.chain_id,
            "from": account,
            "value": contribution_amount,
            "nonce": self.w3.eth.get_transaction_count(account),
            "gasPrice": self.w3.eth.gas_price
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)
    
    def distribute_pot(self, admin_account, private_key):
        """Chủ hụi phân phối tiền cho người nhận hụi đã được chọn"""
        transaction = self.contract.functions.traTienHui().build_transaction({
            "chainId": self.w3.eth.chain_id,
            "from": admin_account,
            "nonce": self.w3.eth.get_transaction_count(admin_account),
            "gasPrice": self.w3.eth.gas_price
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)
    
    def handle_violations(self, admin_account, private_key):
        """Chủ hụi xử lý vi phạm (không đóng tiền)"""
        transaction = self.contract.functions.xuLyViPham().build_transaction({
            "chainId": self.w3.eth.chain_id,
            "from": admin_account,
            "nonce": self.w3.eth.get_transaction_count(admin_account),
            "gasPrice": self.w3.eth.gas_price
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)
    
    def return_deposits(self, admin_account, private_key):
        """Chủ hụi trả lại tiền ký quỹ khi kết thúc hụi"""
        transaction = self.contract.functions.traLaiTienKyQuy().build_transaction({
            "chainId": self.w3.eth.chain_id,
            "from": admin_account,
            "nonce": self.w3.eth.get_transaction_count(admin_account),
            "gasPrice": self.w3.eth.gas_price
        })
        
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)