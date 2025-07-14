import streamlit as st

def show_transaction_details(tx_receipt):
    """Hiển thị chi tiết về một giao dịch blockchain"""
    with st.expander("Chi tiết giao dịch"):
        st.write(f"**Transaction Hash:** `{tx_receipt.transactionHash.hex()}`")
        st.write(f"**Block Number:** {tx_receipt.blockNumber}")
        st.write(f"**Gas Used:** {tx_receipt.gasUsed}")
        
        # Hiển thị các sự kiện nếu có
        if len(tx_receipt.logs) > 0:
            st.write(f"**Số sự kiện:** {len(tx_receipt.logs)}")
            for i, event in enumerate(tx_receipt.logs):
                st.write(f"**Event {i+1}:** `{event.address}`")
        
        st.write(f"**Trạng thái:** {'Thành công' if tx_receipt.status == 1 else 'Thất bại'}")