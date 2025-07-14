// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract ChoiHui {
    struct ThanhVien {
        address payable diaChi;
        uint256 soLanChamDong;
        bool daHutHui;
        uint256 soTienKeuHui;
        bool daDongTienHui;
        bool laHuiChet;
        uint256 soTienKyQuy;
    }

    address public chuHui;
    uint256 public soThanhVienToiDa;
    uint256 public tienMotKy; // Đơn vị: ETH
    uint256 public tongSoKy;
    uint256 public kyHienTai;
    uint256 public tienKyQuyToiThieu; // Đơn vị: ETH
    address public nguoiNhanHui;
    uint256 public tongTienDaDong;

    mapping(address => ThanhVien) public danhSachHuiVien;
    address[] public danhSachNguoiChoi;

    event ThanhVienThamGia(address thanhVien, uint256 tienKyQuy);
    event HuiVienKeuHui(address thanhVien, uint256 soTienKeuHui);
    event HuiVienHutHui(address thanhVien, uint256 soTien);
    event BiLoaiKhoiHui(address thanhVien);
    event DongTienHui(address thanhVien, uint256 soTien);
    event TraTienHui(address thanhVien, uint256 soTien);
    event ThongBaoNguoiNhanHui(address nguoiNhan, uint256 soTienKeuHui);

    modifier chiChuHui() {
        require(msg.sender == chuHui, "Chi co chu hui moi co quyen!");
        _;
    }

    modifier chiThanhVien() {
        require(
            danhSachHuiVien[msg.sender].diaChi != address(0),
            "Ban khong phai thanh vien!"
        );
        _;
    }

    constructor(uint256 _soThanhVienToiDa, uint256 _tienMotKy) {
        chuHui = msg.sender;
        soThanhVienToiDa = _soThanhVienToiDa;
        tienMotKy = _tienMotKy * 1 ether; // Chuyển đổi sang đơn vị ETH
        tienKyQuyToiThieu = (_tienMotKy / 2) * 1 ether; // Tiền ký quỹ bằng 50% số tiền một kỳ
        tongSoKy = _soThanhVienToiDa;
        kyHienTai = 1;
    }

    function thamGiaHui() public payable {
        require(
            danhSachNguoiChoi.length < soThanhVienToiDa,
            "Hui da day thanh vien!"
        );
        require(
            msg.value == tienKyQuyToiThieu,
            "Ban phai dat coc dung so tien ky quy!"
        );
        require(
            danhSachHuiVien[msg.sender].diaChi == address(0),
            "Ban da la thanh vien!"
        );

        danhSachHuiVien[msg.sender] = ThanhVien({
            diaChi: payable(msg.sender),
            soLanChamDong: 0,
            daHutHui: false,
            soTienKeuHui: 0,
            daDongTienHui: false,
            laHuiChet: false,
            // BỔ SUNG: Lưu tiền ký quỹ
            soTienKyQuy: msg.value
        });

        danhSachNguoiChoi.push(msg.sender);
        emit ThanhVienThamGia(msg.sender, msg.value);
    }

    function traLaiTienKyQuy() public chiChuHui {
        // Ví dụ: chỉ cho phép trả ký quỹ nếu đã qua tất cả các kỳ
        require(kyHienTai > tongSoKy, "Hui chua ket thuc het cac ky!");

        // Duyệt qua tất cả thành viên
        for (uint256 i = 0; i < danhSachNguoiChoi.length; i++) {
            address nguoiChoi = danhSachNguoiChoi[i];
            // Nếu người chơi vẫn còn địa chỉ hợp lệ (không bị loại hẳn)
            if (danhSachHuiVien[nguoiChoi].diaChi != address(0)) {
                uint256 soTien = danhSachHuiVien[nguoiChoi].soTienKyQuy;
                if (soTien > 0) {
                    // Gửi lại tiền ký quỹ
                    payable(nguoiChoi).transfer(soTien);
                    // Đặt về 0 tránh trả lần 2
                    danhSachHuiVien[nguoiChoi].soTienKyQuy = 0;
                }
            }
        }
    }

    function xuLyViPham() public chiChuHui {
        // Giả sử chúng ta kiểm tra xem ai chưa 'daDongTienHui' => vi phạm
        for (uint256 i = 0; i < danhSachNguoiChoi.length; i++) {
            address nguoiChoi = danhSachNguoiChoi[i];
            // Nếu người này chưa đóng tiền và vẫn còn hợp lệ
            if (
                !danhSachHuiVien[nguoiChoi].daDongTienHui &&
                danhSachHuiVien[nguoiChoi].diaChi != address(0)
            ) {
                // Tịch thu ký quỹ
                uint256 tienKyQuy = danhSachHuiVien[nguoiChoi].soTienKyQuy;
                if (tienKyQuy > 0) {
                    tongTienDaDong += tienKyQuy;
                    danhSachHuiVien[nguoiChoi].soTienKyQuy = 0;
                }
                // Loại khỏi hợp đồng
                danhSachHuiVien[nguoiChoi].diaChi = payable(address(0));
                // Gửi sự kiện
                emit BiLoaiKhoiHui(nguoiChoi);
            }
        }
    }

    function keuHui(uint256 bidAmount) public chiThanhVien {
        require(
            !danhSachHuiVien[msg.sender].daHutHui,
            "Ban da hut hui, khong the keu hui!"
        );
        require(kyHienTai <= tongSoKy, "Hui da ket thuc!");
        require(
            bidAmount * 1 ether < tienMotKy,
            "So tien keu hui phai nho hon tien mot ky!"
        );

        danhSachHuiVien[msg.sender].soTienKeuHui = bidAmount * 1 ether;
        emit HuiVienKeuHui(msg.sender, bidAmount * 1 ether);
    }

    function chonNguoiNhanHui() public chiChuHui {
        require(nguoiNhanHui == address(0), "Nguoi nhan hui da duoc chon!");

        uint256 maxBid = 0;
        address lastMember;
        uint256 countHuiChet = 0;

        for (uint256 i = 0; i < danhSachNguoiChoi.length; i++) {
            address nguoiChoi = danhSachNguoiChoi[i];
            if (danhSachHuiVien[nguoiChoi].daHutHui) {
                countHuiChet++;
            } else {
                lastMember = nguoiChoi;
            }

            if (
                !danhSachHuiVien[nguoiChoi].daHutHui &&
                danhSachHuiVien[nguoiChoi].soTienKeuHui > maxBid
            ) {
                maxBid = danhSachHuiVien[nguoiChoi].soTienKeuHui;
                nguoiNhanHui = nguoiChoi;
            }
        }

        if (countHuiChet == soThanhVienToiDa - 1) {
            nguoiNhanHui = lastMember;
            // Đánh dấu đây là kỳ hụi chót
            for (uint256 i = 0; i < danhSachNguoiChoi.length; i++) {
                address nguoiChoi = danhSachNguoiChoi[i];
                if (danhSachHuiVien[nguoiChoi].daHutHui) {
                    danhSachHuiVien[nguoiChoi].laHuiChet = true;
                }
            }
        }

        emit ThongBaoNguoiNhanHui(
            nguoiNhanHui,
            danhSachHuiVien[nguoiNhanHui].soTienKeuHui
        );
    }

    function dongTienHui() public payable chiThanhVien {
        require(nguoiNhanHui != address(0), "Chua chon nguoi nhan hui!");
        require(
            !danhSachHuiVien[msg.sender].daDongTienHui,
            "Ban da dong tien ky nay!"
        );
        require(
            msg.sender != nguoiNhanHui,
            "Nguoi nhan hui khong can dong tien!"
        );

        uint256 soTienDong;
        if (danhSachHuiVien[msg.sender].laHuiChet) {
            // Người đã nhận hụi, trong kỳ hụi chót sẽ đóng đủ tiền một kỳ
            soTienDong = tienMotKy;
        } else {
            // Người chưa nhận hụi, đóng tiền thông thường (trừ đi số tiền kêu hụi)
            soTienDong = tienMotKy - danhSachHuiVien[nguoiNhanHui].soTienKeuHui;
        }

        require(msg.value == soTienDong, "Sai so tien can dong!");
        danhSachHuiVien[msg.sender].daDongTienHui = true;
        tongTienDaDong += msg.value;
        emit DongTienHui(msg.sender, msg.value);
    }

    function traTienHui() public chiChuHui {
        // Kiểm tra xem đã đủ tiền để trả cho người nhận hụi chưa
        require(nguoiNhanHui != address(0), "Chua co nguoi nhan hui!");

        // Tính toán tổng tiền cần đóng dựa trên số người đã đóng tiền
        uint256 tongTienCanDong = 0;
        uint256 soNguoiHuiChet = 0;

        for (uint256 i = 0; i < danhSachNguoiChoi.length; i++) {
            address nguoiChoi = danhSachNguoiChoi[i];
            if (nguoiChoi != nguoiNhanHui) {
                if (danhSachHuiVien[nguoiChoi].laHuiChet) {
                    tongTienCanDong += tienMotKy;
                    soNguoiHuiChet++;
                } else {
                    tongTienCanDong += (tienMotKy -
                        danhSachHuiVien[nguoiNhanHui].soTienKeuHui);
                }
            }
        }

        require(tongTienDaDong >= tongTienCanDong, "Chua du tien de tra!");
        payable(nguoiNhanHui).transfer(tongTienDaDong);

        danhSachHuiVien[nguoiNhanHui].daHutHui = true;
        danhSachHuiVien[nguoiNhanHui].laHuiChet = true;
        emit TraTienHui(nguoiNhanHui, tongTienDaDong);

        // Reset kỳ hụi mới
        nguoiNhanHui = address(0);
        tongTienDaDong = 0;

        for (uint256 i = 0; i < danhSachNguoiChoi.length; i++) {
            danhSachHuiVien[danhSachNguoiChoi[i]].daDongTienHui = false;
        }

        kyHienTai++;
    }
}
