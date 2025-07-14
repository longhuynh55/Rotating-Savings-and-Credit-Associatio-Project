import streamlit as st
import sys
import os

# Thêm thư mục cha vào path để import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.contract_interact import ChoiHuiContract

def app():
    st.title("ChoiHui - Hụi Blockchain")
    
    # Kiểm tra xem contract đã được triển khai chưa
    contract_deployed = os.path.exists("backend/data/contract_address.txt")
    
    if not contract_deployed:
        st.info("Chào mừng đến với ứng dụng ChoiHui DApp!")
        st.write("""
        Đây là ứng dụng blockchain triển khai hệ thống Hụi - một hình thức tiết kiệm và tín dụng quay vòng truyền thống.
        
        ### Cách hoạt động:
        1. Thành viên đóng tiền vào quỹ chung mỗi kỳ
        2. Mỗi kỳ, một thành viên nhận được toàn bộ số tiền trong quỹ
        3. Các thành viên đấu giá (kêu hụi) để được chọn nhận tiền
        4. Người có mức kêu hụi cao nhất sẽ được chọn
        
        ### Để bắt đầu:
        Vui lòng triển khai smart contract bằng cách nhấn nút "Triển khai Smart Contract" ở thanh bên trái.
        """)
        return
    
    # Kết nối tới contract
    try:
        contract = ChoiHuiContract()
        
        # Hiển thị thông tin contract
        contract_info = contract.get_contract_info()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Thông tin hụi")
            st.write(f"**Chủ hụi:** `{contract_info['chu_hui'][:10]}...`")
            st.write(f"**Số thành viên tối đa:** {contract_info['so_thanh_vien_toi_da']}")
            st.write(f"**Tiền mỗi kỳ:** {contract_info['tien_mot_ky']} ETH")
            st.write(f"**Tiền ký quỹ:** {contract_info['tien_ky_quy']} ETH")
        
        with col2:
            st.subheader("Trạng thái hiện tại")
            st.write(f"**Kỳ hiện tại:** {contract_info['ky_hien_tai']}/{contract_info['tong_so_ky']}")
            
            current_recipient = contract.get_current_recipient()
            if current_recipient:
                st.write(f"**Người nhận hụi hiện tại:** `{current_recipient[:10]}...`")
            else:
                st.write("**Chưa chọn người nhận hụi cho kỳ này**")
        
        # Hiển thị danh sách thành viên
        st.subheader("Danh sách thành viên")
        members = contract.get_member_list()
        
        if members:
            for i, member in enumerate(members):
                with st.expander(f"Thành viên {i+1}: {member['dia_chi'][:10]}..."):
                    st.write(f"Địa chỉ: `{member['dia_chi']}`")
                    st.write(f"Đã nhận hụi: {'Có' if member['da_hut_hui'] else 'Chưa'}")
                    st.write(f"Mức kêu hụi hiện tại: {member['so_tien_keu_hui']} ETH")
                    st.write(f"Đã đóng tiền kỳ này: {'Có' if member['da_dong_tien_hui'] else 'Chưa'}")
                    st.write(f"Đang ở kỳ hụi chót: {'Có' if member['la_hui_chet'] else 'Không'}")
                    st.write(f"Tiền ký quỹ: {member['tien_ky_quy']} ETH")
        else:
            st.info("Chưa có thành viên nào tham gia")

        # Hiển thị thông tin về ứng dụng
        st.markdown("---")
        st.subheader("Về ứng dụng ChoiHui DApp")
        st.write("""
        **ChoiHui DApp** là ứng dụng phi tập trung triển khai hệ thống hụi truyền thống trên blockchain Ethereum.
        
        ### Các chức năng:
        - **Tham gia hụi**: Thành viên đặt cọc tiền ký quỹ để tham gia
        - **Kêu hụi**: Đấu thầu để nhận được tiền hụi trong kỳ hiện tại
        - **Đóng tiền hụi**: Đóng góp tiền vào quỹ chung mỗi kỳ
        - **Quản lý hụi**: Chủ hụi có các chức năng quản lý đặc biệt
        
        ### Công nghệ sử dụng:
        - Smart Contract (Solidity)
        - Web3.py
        - Streamlit
        - Ganache (local blockchain)
        """)
    
    except Exception as e:
        st.error(f"Lỗi kết nối đến contract: {str(e)}")
        st.info("Đảm bảo Ganache đang chạy và contract đã được triển khai")