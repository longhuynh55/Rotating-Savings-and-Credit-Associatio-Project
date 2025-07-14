import streamlit as st
import sys
import os

# Thêm thư mục cha vào path để import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.contract_interact import ChoiHuiContract
from frontend.utils.display import show_transaction_details

def app():
    st.title("Tham gia hụi")
    
    try:
        contract = ChoiHuiContract()
        contract_info = contract.get_contract_info()
        
        st.write(f"Số tiền ký quỹ cần đóng: **{contract_info['tien_ky_quy']} ETH**")
        
        # Lấy danh sách tài khoản hiện có
        accounts = contract.get_accounts()
        
        # Hiển thị danh sách thành viên hiện tại
        members = contract.get_member_list()
        if members:
            st.subheader("Danh sách thành viên hiện tại")
            for i, member in enumerate(members):
                st.write(f"{i+1}. `{member['dia_chi'][:10]}...{member['dia_chi'][-8:]}`")
        
        # Kiểm tra xem còn slot không
        if len(members) >= contract_info['so_thanh_vien_toi_da']:
            st.warning(f"Hụi đã đủ thành viên (tối đa {contract_info['so_thanh_vien_toi_da']} thành viên)")
            return
        
        st.subheader("Đăng ký tham gia")
        
        # Lọc các tài khoản chưa tham gia
        member_addresses = [m['dia_chi'] for m in members]
        available_accounts = [acc for acc in accounts if acc not in member_addresses]
        
        if not available_accounts:
            st.warning("Tất cả tài khoản đã tham gia hụi")
            return
        
        # Chọn tài khoản
        selected_account = st.selectbox(
            "Chọn tài khoản", 
            available_accounts,
            format_func=lambda x: f"{x[:10]}...{x[-8:]} ({contract.w3.eth.get_balance(x) / 10**18:.4f} ETH)"
        )
        
        # Nhập private key
        # Trong ứng dụng thực tế, cần xử lý bảo mật hơn
        private_key = st.text_input("Nhập Private Key", type="password", 
                                   help="Trong môi trường thử nghiệm với Ganache, private key mặc định cho account[0] là: 0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d")
        
        if st.button("Tham gia hụi"):
            if not private_key:
                st.error("Vui lòng nhập private key")
            else:
                try:
                    with st.spinner("Đang tham gia hụi..."):
                        tx_receipt = contract.join_hui(selected_account, private_key)
                        st.success(f"Tham gia thành công!")
                        show_transaction_details(tx_receipt)
                except Exception as e:
                    st.error(f"Lỗi khi tham gia hụi: {str(e)}")
        
        # Thông tin hướng dẫn
        with st.expander("Thông tin về hệ thống hụi"):
            st.write("""
            ### Hệ thống hụi hoạt động như thế nào?
            
            1. **Tham gia**: Mỗi thành viên đặt cọc một khoản tiền ký quỹ để tham gia.
            2. **Kêu hụi**: Mỗi kỳ, thành viên có thể đấu thầu (kêu hụi) để nhận quỹ.
            3. **Đóng tiền**: Sau khi chủ hụi chọn người nhận hụi, các thành viên khác đóng tiền vào quỹ.
            4. **Nhận tiền**: Người được chọn nhận toàn bộ tiền trong quỹ.
            
            ### Lợi ích của hụi blockchain:
            - **Minh bạch**: Mọi giao dịch đều được ghi lại trên blockchain
            - **Tự động**: Smart contract tự động thực hiện các quy tắc của hụi
            - **An toàn**: Tiền ký quỹ đảm bảo thành viên không bỏ hụi giữa chừng
            """)
    
    except Exception as e:
        st.error(f"Lỗi kết nối đến contract: {str(e)}")
        st.info("Đảm bảo Ganache đang chạy và contract đã được triển khai")