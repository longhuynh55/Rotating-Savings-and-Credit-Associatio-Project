import os
import sys
import subprocess

def create_directory_structure():
    """Tạo cấu trúc thư mục dự án"""
    directories = [
        "contracts",
        "backend",
        "backend/data",
        "frontend",
        "frontend/pages",
        "frontend/utils",
        "scripts"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # Tạo file __init__.py trong mỗi package Python
        if "backend" in directory or "frontend" in directory:
            init_path = os.path.join(directory, "__init__.py")
            if not os.path.exists(init_path):
                with open(init_path, "w") as f:
                    f.write("# Package initialization file\n")
    
    print("Đã tạo cấu trúc thư mục dự án.")

def install_dependencies():
    """Cài đặt các dependencies"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Đã cài đặt các thư viện cần thiết.")
    except subprocess.CalledProcessError:
        print("Lỗi khi cài đặt thư viện. Vui lòng cài đặt thủ công: pip install -r requirements.txt")

def check_ganache():
    """Kiểm tra Ganache đã được cài đặt và chạy chưa"""
    try:
        # Kiểm tra kết nối đến Ganache
        from web3 import Web3
        web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
        if web3.is_connected():
            print("Ganache đang chạy ở địa chỉ http://127.0.0.1:7545")
            return True
        else:
            print("Không thể kết nối đến Ganache. Vui lòng kiểm tra lại.")
            return False
    except Exception as e:
        print(f"Lỗi khi kiểm tra Ganache: {str(e)}")
        return False

def setup():
    """Thiết lập ban đầu cho dự án"""
    print("Đang thiết lập dự án ChoiHui DApp...")
    
    # Tạo cấu trúc thư mục
    create_directory_structure()
    
    # Cài đặt dependencies
    install_dependencies()
    
    # Kiểm tra Ganache
    if check_ganache():
        print("Thiết lập dự án ChoiHui DApp đã hoàn tất.")
        print("\nHướng dẫn chạy ứng dụng:")
        print("1. Đảm bảo Ganache đang chạy")
        print("2. Chạy ứng dụng Streamlit: streamlit run frontend/app.py")
        print("3. Truy cập ứng dụng tại địa chỉ: http://localhost:8501")
    else:
        print("\nLưu ý: Bạn cần cài đặt và chạy Ganache Desktop trước khi sử dụng ứng dụng.")
        print("Tải Ganache từ: https://trufflesuite.com/ganache/")

if __name__ == "__main__":
    setup()