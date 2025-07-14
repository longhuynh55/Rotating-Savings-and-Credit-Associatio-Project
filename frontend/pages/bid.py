import streamlit as st
import sys
import os

# Thêm thư mục cha vào path để import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.contract_interact import ChoiHuiContract
from frontend.utils.display import show_transaction_details

def app():
    st.title("Kêu hụi (Đấu thầu)")
    
    try:
        contract = ChoiHuiContract()
        contract_info = contract.get_contract_info()
        
        # Kiểm tra xem đã có người nhận hụi cho kỳ này chưa
        current_recipient = contract.get_current_recipient()
        if current_recipient:
            st.warning(f"Đã chọn người nhận hụi cho kỳ này: `{current_recipient[:10]}...`")
            st.info("Vui lòng đợi đến kỳ sau để kêu hụi")
            return
        
        # Lấy danh sách thành viên
        members = contract.get_member_list()
        
        # Hiển thị các mức kêu hụi hiện tại
        st.subheader("Các mức kêu hụi hiện tại")
        has_bids = False
        for member in members:
            if member["so_tien_keu_hui"] > 0:
                has_bids = True
                st.write(f"`{member['dia_chi'][:10]}...`: {member['so_tien_keu_hui']} ETH")
        
        if not has_bids:
            st.info("Chưa có ai kêu hụi cho kỳ này")
        
        st.subheader("Kêu hụi mới")
        
        # Lọc các tài khoản đã tham gia nhưng chưa hút hụi
        member_addresses = [m['dia_chi'] for m in members if not m['da_hut_hui']]
        
        if not member_addresses:
            st.warning("Không có thành viên nào có thể kêu hụi")
            return
        
        # Chọn tài khoản
        selected_account = st.selectbox(
            "Chọn tài khoản", 
            member_addresses,
            format_func=lambda x: f"{x[:10]}...{x[-8:]} ({contract.w3.eth.get_balance(x) / 10**18:.4f} ETH)"
        )
        
        # Maximum bid allowed is less than the contribution amount
        max_bid = float(contract_info["tien_mot_ky"]) - 0.01
        
        # Mức kêu hụi
        bid_amount = st.slider(
            "Mức kêu hụi (ETH)", 
            min_value=0.0, 
            max_value=max_bid, 
            step=0.1, 
            value=0.5,
            help="Mức kêu hụi là số tiền bạn sẵn sàng bớt đi từ quỹ hụi. Mức càng cao càng có khả năng được chọn."
        )
        
        # Nhập private key
        private_key = st.text_input("Nhập Private Key", type="password")
        
        if st.button("Gửi kêu hụi"):
            if not private_key:
                st.error("Vui lòng nhập private key")
            else:
                try:
                    with st.spinner("Đang gửi kêu hụi..."):
                        tx_receipt = contract.bid_for_hui(selected_account, private_key, bid_amount)
                        st.success(f"Kêu hụi thành công!")
                        show_transaction_details(tx_receipt)
                except Exception as e:
                    st.error(f"Lỗi khi kêu hụi: {str(e)}")
        
        # Giải thích về kêu hụi
        with st.expander("Kêu hụi là gì?"):
            st.write("""
            ### Cơ chế kêu hụi
            
            Kêu hụi là hình thức đấu thầu để được nhận tiền từ quỹ hụi trong kỳ hiện tại.
            
            **Cách hoạt động:**
            1. Mỗi thành viên đưa ra mức kêu hụi - số tiền họ sẵn sàng bớt từ tổng số tiền quỹ
            2. Người có mức kêu hụi cao nhất sẽ được chọn làm người nhận hụi
            3. Các thành viên khác chỉ cần đóng (Tiền một kỳ - Mức kêu hụi) ETH
            4. Người nhận hụi sẽ nhận được tổng số tiền đã đóng
            
            **Ví dụ:** Nếu tiền một kỳ là 1 ETH và bạn kêu hụi 0.2 ETH:
            - Nếu được chọn, các thành viên khác chỉ cần đóng 0.8 ETH
            - Bạn nhận được tổng số tiền từ các thành viên đóng
            
            Mức kêu hụi cao hơn sẽ tăng khả năng được chọn, nhưng cũng giảm số tiền nhận được.
            """)
    
    except Exception as e:
        st.error(f"Lỗi kết nối đến contract: {str(e)}")
        st.info("Đảm bảo Ganache đang chạy và contract đã được triển khai")