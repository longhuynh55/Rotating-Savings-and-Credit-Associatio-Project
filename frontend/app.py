import streamlit as st
import sys
import os
from web3 import Web3
import streamlit as st
# Thêm thư mục cha vào path để import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.pages import home, join, bid, contribute, admin
from backend.deploy import deploy_contract

def main():
    st.sidebar.title("ChoiHui DApp - Hụi Blockchain")
    
    # Kiểm tra xem contract đã được triển khai chưa
    contract_deployed = os.path.exists("backend/data/contract_address.txt")
    
    if not contract_deployed:
        st.sidebar.warning("Smart contract chưa được triển khai.")
        if st.sidebar.button("Triển khai Smart Contract"):
            # Hiển thị form triển khai
            with st.form("deploy_form"):
                st.subheader("Triển khai Smart Contract")
                max_members = st.number_input("Số thành viên tối đa", min_value=2, max_value=20, value=5)
                contribution_amount = st.number_input("Số tiền mỗi kỳ (ETH)", min_value=0.1, max_value=10.0, value=1.0)
                private_key = st.text_input("Private key (nếu không nhập sẽ dùng mặc định của Ganache)", type="password")
                
                submitted = st.form_submit_button("Triển khai")
                if submitted:
                    if not private_key:
                        private_key = None
                    with st.spinner("Đang triển khai smart contract..."):
                        address, message = deploy_contract(
                            max_members=int(max_members),
                            contribution_amount=int(contribution_amount),
                            private_key=private_key
                        )
                    
                    if address:
                        st.success(message)
                        st.experimental_rerun()
                    else:
                        st.error(message)
    
    # Các trang ứng dụng
    pages = {
        "Trang chủ": home,
        "Tham gia hụi": join,
        "Kêu hụi": bid,
        "Đóng tiền hụi": contribute,
        "Quản lý hụi": admin
    }
    
    # Navigation trong sidebar
    selection = st.sidebar.radio("Chọn trang", list(pages.keys()))
    
    # Hiển thị trang đã chọn
    if contract_deployed or selection == "Trang chủ":
        page = pages[selection]
        page.app()
    else:
        st.info("Vui lòng triển khai smart contract trước khi sử dụng các chức năng khác.")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info(
        "Ứng dụng phi tập trung (DApp) triển khai hệ thống hụi truyền thống trên blockchain."
    )

if __name__ == "__main__":
    main()