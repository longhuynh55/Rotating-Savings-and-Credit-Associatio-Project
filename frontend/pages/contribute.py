import streamlit as st
import sys
import os

# Thêm thư mục cha vào path để import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.contract_interact import ChoiHuiContract
from frontend.utils.display import show_transaction_details

def app():
    st.title("Đóng tiền hụi")
    
    try:
        contract = ChoiHuiContract()
        
        # Kiểm tra xem đã chọn người nhận hụi chưa
        recipient = contract.get_current_recipient()
        
        if not recipient:
            st.warning("Chưa có người nhận hụi cho kỳ này. Vui lòng đợi chủ hụi chọn người nhận hụi.")
            return
        
        # Lấy thông tin người nhận hụi
        recipient_info = contract.contract.functions.danhSachHuiVien(recipient).call()
        bid_amount = contract.w3.from_wei(recipient_info[3], "ether")  # soTienKeuHui
        
        st.subheader("Thông tin kỳ hụi hiện tại")
        st.write(f"**Người nhận hụi:** `{recipient[:10]}...{recipient[-8:]}`")
        st.write(f"**Mức kêu hụi:** {bid_amount} ETH")
        
        # Lấy thông tin contract
        contract_info = contract.get_contract_info()
        base_amount = float(contract_info["tien_mot_ky"])
        
        # Lấy danh sách thành viên
        members = contract.get_member_list()
        
        # Hiển thị trạng thái đóng tiền
        st.subheader("Trạng thái đóng tiền")
        for member in members:
            if member["dia_chi"] == recipient:
                st.write(f"`{member['dia_chi'][:10]}...`: Người nhận hụi (không cần đóng)")
            else:
                status = "✅ Đã đóng" if member["da_dong_tien_hui"] else "❌ Chưa đóng"
                st.write(f"`{member['dia_chi'][:10]}...`: {status}")
        
        st.subheader("Đóng tiền hụi")
        
        # Lọc các tài khoản đã tham gia, không phải người nhận hụi và chưa đóng tiền
        member_addresses = [
            m['dia_chi'] for m in members 
            if m['dia_chi'] != recipient and not m['da_dong_tien_hui']
        ]
        
        if not member_addresses:
            st.success("Tất cả thành viên đã đóng tiền hoặc bạn là người nhận hụi!")
            return
        
        # Chọn tài khoản
        selected_account = st.selectbox(
            "Chọn tài khoản", 
            member_addresses,
            format_func=lambda x: f"{x[:10]}...{x[-8:]} ({contract.w3.eth.get_balance(x) / 10**18:.4f} ETH)"
        )
        
        # Tính số tiền cần đóng
        selected_member = next(m for m in members if m['dia_chi'] == selected_account)
        contribution_amount = base_amount
        if not selected_member["la_hui_chet"]:
            contribution_amount = base_amount - float(bid_amount)
        
        st.write(f"**Số tiền cần đóng:** {contribution_amount} ETH")
        
        # Nhập private key
        private_key = st.text_input("Nhập Private Key", type="password")
        
        if st.button("Đóng tiền"):
            if not private_key:
                st.error("Vui lòng nhập private key")
            else:
                try:
                    with st.spinner("Đang đóng tiền..."):
                        tx_receipt = contract.contribute(selected_account, private_key)
                        st.success(f"Đóng tiền thành công!")
                        show_transaction_details(tx_receipt)
                except Exception as e:
                    st.error(f"Lỗi khi đóng tiền: {str(e)}")
        
        # Giải thích về đóng tiền hụi
        with st.expander("Hướng dẫn đóng tiền hụi"):
            st.write("""
            ### Cách đóng tiền hụi
            
            Sau khi chủ hụi đã chọn người nhận hụi, các thành viên khác cần đóng tiền vào quỹ.
            
            **Số tiền cần đóng:**
            - Nếu bạn chưa từng nhận hụi: (Tiền một kỳ - Mức kêu hụi) ETH
            - Nếu bạn đã nhận hụi và đang ở kỳ hụi chót: Đóng đủ tiền một kỳ ETH
            
            **Lưu ý:**
            - Nếu không đóng tiền đúng hạn, bạn có thể bị xử lý vi phạm
            - Tiền ký quỹ có thể bị tịch thu nếu vi phạm nhiều lần
            """)
    
    except Exception as e:
        st.error(f"Lỗi kết nối đến contract: {str(e)}")
        st.info("Đảm bảo Ganache đang chạy và contract đã được triển khai")