import streamlit as st
import sys
import os

# Thêm thư mục cha vào path để import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.contract_interact import ChoiHuiContract
from frontend.utils.display import show_transaction_details

def app():
    st.title("Quản lý hụi")
    
    try:
        contract = ChoiHuiContract()
        
        # Lấy thông tin contract
        contract_info = contract.get_contract_info()
        admin_address = contract_info["chu_hui"]
        
        st.write(f"**Chủ hụi:** `{admin_address}`")
        st.write(f"**Kỳ hiện tại:** {contract_info['ky_hien_tai']}/{contract_info['tong_so_ky']}")
        
        # Lấy danh sách tài khoản
        accounts = contract.get_accounts()
        
        # Chọn tài khoản
        selected_account = st.selectbox(
            "Chọn tài khoản chủ hụi", 
            accounts,
            format_func=lambda x: f"{x[:10]}...{x[-8:]} ({contract.w3.eth.get_balance(x) / 10**18:.4f} ETH)"
        )
        
        # Kiểm tra quyền admin
        is_admin = (selected_account == admin_address)
        if not is_admin:
            st.warning("Tài khoản đã chọn không phải là chủ hụi. Các chức năng quản lý sẽ không hoạt động.")
        
        # Nhập private key
        private_key = st.text_input("Nhập Private Key chủ hụi", type="password")
        
        # Chức năng quản lý
        st.subheader("Chức năng quản lý")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Chọn người nhận hụi
            recipient = contract.get_current_recipient()
            if recipient:
                st.info(f"Người nhận hụi đã được chọn: `{recipient[:10]}...`")
            else:
                if st.button("Chọn người nhận hụi"):
                    if not private_key:
                        st.error("Vui lòng nhập private key")
                    else:
                        try:
                            with st.spinner("Đang chọn người nhận hụi..."):
                                tx_receipt = contract.select_recipient(selected_account, private_key)
                                new_recipient = contract.get_current_recipient()
                                if new_recipient:
                                    st.success(f"Đã chọn người nhận hụi: `{new_recipient[:10]}...`")
                                    show_transaction_details(tx_receipt)
                                else:
                                    st.error("Không thể chọn người nhận hụi")
                        except Exception as e:
                            st.error(f"Lỗi khi chọn người nhận hụi: {str(e)}")
            
            # Phân phối tiền hụi
            if st.button("Phân phối tiền hụi"):
                if not private_key:
                    st.error("Vui lòng nhập private key")
                elif not recipient:
                    st.error("Chưa chọn người nhận hụi")
                else:
                    try:
                        with st.spinner("Đang phân phối tiền hụi..."):
                            tx_receipt = contract.distribute_pot(selected_account, private_key)
                            st.success(f"Phân phối tiền hụi thành công!")
                            show_transaction_details(tx_receipt)
                    except Exception as e:
                        st.error(f"Lỗi khi phân phối tiền hụi: {str(e)}")
        
        with col2:
            # Xử lý vi phạm
            if st.button("Xử lý vi phạm"):
                if not private_key:
                    st.error("Vui lòng nhập private key")
                else:
                    try:
                        with st.spinner("Đang xử lý vi phạm..."):
                            tx_receipt = contract.handle_violations(selected_account, private_key)
                            st.success(f"Xử lý vi phạm thành công!")
                            show_transaction_details(tx_receipt)
                    except Exception as e:
                        st.error(f"Lỗi khi xử lý vi phạm: {str(e)}")
            
            # Trả lại tiền ký quỹ
            if st.button("Trả lại tiền ký quỹ"):
                if not private_key:
                    st.error("Vui lòng nhập private key")
                else:
                    if contract_info["ky_hien_tai"] <= contract_info["tong_so_ky"]:
                        st.warning("Hụi chưa kết thúc. Không thể trả lại tiền ký quỹ.")
                    else:
                        try:
                            with st.spinner("Đang trả lại tiền ký quỹ..."):
                                tx_receipt = contract.return_deposits(selected_account, private_key)
                                st.success(f"Trả lại tiền ký quỹ thành công!")
                                show_transaction_details(tx_receipt)
                        except Exception as e:
                            st.error(f"Lỗi khi trả lại tiền ký quỹ: {str(e)}")
        
        # Hiển thị trạng thái thành viên
        st.subheader("Trạng thái thành viên")
        members = contract.get_member_list()
        
        if members:
            for i, member in enumerate(members):
                with st.expander(f"Thành viên {i+1}: {member['dia_chi'][:10]}..."):
                    st.write(f"Địa chỉ: `{member['dia_chi']}`")
                    st.write(f"Đã nhận hụi: {'Có' if member['da_hut_hui'] else 'Chưa'}")
                    st.write(f"Mức kêu hụi: {member['so_tien_keu_hui']} ETH")
                    st.write(f"Đã đóng tiền kỳ này: {'Có' if member['da_dong_tien_hui'] else 'Chưa'}")
                    st.write(f"Đang ở kỳ hụi chót: {'Có' if member['la_hui_chet'] else 'Không'}")
                    st.write(f"Tiền ký quỹ: {member['tien_ky_quy']} ETH")
        else:
            st.info("Chưa có thành viên nào tham gia")
        
        # Hướng dẫn quản lý
        with st.expander("Hướng dẫn quản lý hụi"):
            st.write("""
            ### Vai trò của chủ hụi
            
            Chủ hụi có các trách nhiệm và quyền hạn sau:
            
            **1. Chọn người nhận hụi**: 
            - Xác định người có mức kêu hụi cao nhất làm người nhận hụi
            - Nếu có nhiều người cùng mức, chủ hụi quyết định
            
            **2. Phân phối tiền hụi**:
            - Sau khi đủ thành viên đóng tiền, chuyển toàn bộ tiền cho người nhận hụi
            - Bắt đầu kỳ hụi mới
            
            **3. Xử lý vi phạm**:
            - Kiểm tra thành viên nào chưa đóng tiền
            - Tịch thu tiền ký quỹ của thành viên vi phạm
            
            **4. Trả lại tiền ký quỹ**:
            - Khi hụi kết thúc, trả lại tiền ký quỹ cho các thành viên
            - Chỉ thực hiện được khi đã hoàn thành tất cả các kỳ
            """)
    
    except Exception as e:
        st.error(f"Lỗi kết nối đến contract: {str(e)}")
        st.info("Đảm bảo Ganache đang chạy và contract đã được triển khai")