# -*- coding: utf-8 -*-
"""
Cập nhật file Word Kịch bản Thuyết trình với ngôn từ phổ thông, dễ hiểu,
bổ sung chú thích giải thích trong dấu ngoặc đơn (),
và giữ nguyên 100% phần chú giải chi tiết của người dùng ở Slide 4.
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_friendly_script_docx():
    doc = docx.Document()

    for sec in doc.sections:
        sec.top_margin = Inches(1)
        sec.bottom_margin = Inches(1)
        sec.left_margin = Inches(1)
        sec.right_margin = Inches(1)

    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Times New Roman'
    font.size = Pt(11)
    font.color.rgb = RGBColor(20, 20, 20)
    style_normal.paragraph_format.line_spacing = 1.25
    style_normal.paragraph_format.space_after = Pt(4)

    # Tiêu đề tài liệu
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_title.add_run("KỊCH BẢN THUYẾT TRÌNH BÁO CÁO KHOA HỌC\n(DIỄN ĐẠT DỄ HIỂU - KÈM CHÚ THÍCH THUẬT NGỮ)")
    r_t.font.name = "Times New Roman"
    r_t.font.size = Pt(15)
    r_t.font.bold = True
    r_t.font.color.rgb = RGBColor(15, 23, 42)

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_after = Pt(16)
    r_m = p_meta.add_run(
        "Đề tài: Nghiên cứu và đánh giá toàn diện các kiến trúc học sâu phân đoạn đa mô hình khối u não trên ảnh cộng hưởng từ kết hợp tối ưu hóa ranh giới lâm sàng\n"
        "Tác giả: Trần Mạnh Hùng | Giảng viên hướng dẫn: ThS. Hoàng Văn Quý\n"
        "Đơn vị: Phân hiệu Trường Đại học Thủy Lợi, TP. Hồ Chí Minh | Thời lượng dự kiến: 15 - 20 phút\n"
        "(Các thuật ngữ chuyên môn đều được bổ sung lời giải thích phổ thông trong dấu ngoặc đơn để dễ nói và dễ hiểu)"
    )
    r_m.font.name = "Times New Roman"
    r_m.font.size = Pt(10)
    r_m.font.italic = True
    r_m.font.color.rgb = RGBColor(70, 70, 70)

    slides_content = [
        {
            "num": 1,
            "title": "Slide 1: Trang tiêu đề công trình nghiên cứu",
            "time": "1.0 phút",
            "screen": "Tiêu đề đề tài, tác giả Trần Mạnh Hùng, GVHD Hoàng Văn Quý, đơn vị Phân hiệu ĐH Thủy Lợi.",
            "speech": (
                "Kính thưa quý Thầy Cô trong Hội đồng chấm đề tài khoa học và toàn thể quý vị đang có mặt trong buổi báo cáo ngày hôm nay.\n\n"
                "Em tên là Trần Mạnh Hùng, sinh viên chuyên ngành Công nghệ Thông tin, Phân hiệu Trường Đại học Thủy Lợi. Hôm nay, dưới sự hướng dẫn khoa học của Thầy Hoàng Văn Quý, em xin trân trọng trình bày báo cáo công trình nghiên cứu với đề tài: 'Nghiên cứu và đánh giá toàn diện các kiến trúc học sâu phân đoạn đa mô hình khối u não trên ảnh cộng hưởng từ kết hợp tối ưu hóa ranh giới lâm sàng'.\n\n"
                "Nói một cách đơn giản và dễ hiểu, đề tài của chúng em tập trung giải quyết bài toán: Làm thế nào để máy tính (trí tuệ nhân tạo) có thể tự động nhìn vào các tấm ảnh chụp não (MRI), vừa quét thật nhanh qua hàng trăm lát cắt để phát hiện xem có khối u hay không, vừa tự động vẽ khoanh vùng chính xác từng milimet đường viền khối u để bác sĩ phẫu thuật cắt bỏ u an toàn mà không làm tổn thương các vùng não lành xung quanh; đồng thời phần mềm có thể tự in ra một phiếu kết quả chẩn đoán y tế hoàn chỉnh cho bác sĩ sử dụng. Sau đây, em xin phép được bắt đầu phần trình bày chi tiết."
            )
        },
        {
            "num": 2,
            "title": "Slide 2: Thực trạng lâm sàng & Thách thức trong phân đoạn u não MRI",
            "time": "1.5 phút",
            "screen": "Bối cảnh lâm sàng (80-120 lát cắt, sai lệch 15-25%) và 3 rào cản kỹ thuật thị giác máy tính.",
            "speech": (
                "Kính thưa Hội đồng, chụp cộng hưởng từ (MRI) hiện nay được coi là 'tiêu chuẩn vàng' (tức là phương pháp tốt nhất và đáng tin cậy nhất) trong chẩn đoán các bệnh lý trong não vì ảnh chụp rất rõ các mô mềm và hoàn toàn không gây nhiễm xạ độc hại (không có tia X như khi chụp cắt lớp CT).\n\n"
                "Tuy nhiên, trên thực tế tại các bệnh viện, mỗi ca chụp não thường có từ 80 đến 120 tấm ảnh chụp lát cắt. Các bác sĩ phải ngồi nhìn từng tấm ảnh một và dùng chuột khoanh vùng thủ công khối u, việc này tốn rất nhiều thời gian và gây mỏi mắt. Các thống kê y khoa cho thấy tỉ lệ chênh lệch khi nhìn nhận ranh giới khối u giữa các bác sĩ dao động từ 15% đến 25% (tức là bác sĩ này nhìn thấy bờ u ở đây, nhưng bác sĩ khác lại nhìn thấy lệch đi một chút).\n\n"
                "Điểm nguy hiểm mang tính chất sinh tử là: ranh giới khối u trong não vô cùng nhạy cảm. Chỉ cần cắt phạm vài milimet vào vùng não lành có thể làm bệnh nhân bị liệt vận động hoặc mất khả năng nói; ngược lại, nếu cắt chừa lại vài milimet tế bào ung thư thì khối u sẽ nhanh chóng tái phát trở lại.\n\n"
                "Dưới góc độ máy tính và học sâu, việc dạy cho máy tính tự khoanh vùng khối u gặp 3 khó khăn rất lớn:\n"
                "Thứ nhất là u não chiếm diện tích quá nhỏ (mất cân bằng diện tích nghiêm trọng): khối u thường chỉ chiếm dưới 5% diện tích của lát cắt, còn lại hơn 95% là phần não lành và nền đen. Do đó, máy tính rất dễ bị 'học vẹt', đoán mò toàn bộ là não lành để đạt điểm cao.\n"
                "Thứ hai là mỗi loại u lại có hình dáng và tính chất hoàn toàn khác nhau: U màng não thì nằm ở màng bên ngoài có vỏ bọc rất rõ; U tuyến yên thì nằm gọn ở đáy sọ; trong khi U thần kinh đệm lại là u ác tính ăn lan, chân u mọc rễ hòa lẫn vào nhu mô não nên ranh giới cực kỳ mờ nhạt.\n"
                "Thứ ba là các công thức tính điểm truyền thống (như hàm Dice Loss) chỉ quan tâm đến tổng diện tích trùng nhau, nên máy tính thường có xu hướng 'làm tròn vo' các góc cạnh của khối u (thuật ngữ chuyên môn gọi là hiện tượng Over-smoothing), dẫn đến việc ranh giới u bị vẽ sai lệch khá nhiều."
            )
        },
        {
            "num": 3,
            "title": "Slide 3: Mục tiêu nghiên cứu & 6 đóng góp học thuật trọng tâm",
            "time": "1.0 phút",
            "screen": "3 cột thẻ: Đối chuẩn kiến trúc, Tiền xử lý & XAI, Ngoại kiểm & CADx.",
            "speech": (
                "Xuất phát từ thực tế đó, nghiên cứu của chúng em đặt ra 6 mục tiêu và đóng góp trọng tâm:\n\n"
                "Về mặt thuật toán: Chúng em thử nghiệm và so sánh đồng thời 6 mô hình trí tuệ nhân tạo khác nhau; đồng thời đưa vào một công thức phạt lỗi đặc biệt gọi là Boundary Loss dựa trên bản đồ khoảng cách dấu (SDF), giúp phạt nặng những điểm đoán sai đường viền, giải quyết triệt để tật làm tròn vo góc cạnh của mô hình.\n\n"
                "Về mặt xử lý ảnh và độ tin cậy: Chúng em xây dựng quy trình tự động bóc bỏ phần xương sọ (Skull Stripping - tức là cắt gọt sạch phần vỏ xương trắng bên ngoài để máy không nhận nhầm xương sọ thành khối u); đồng thời ứng dụng công nghệ bản đồ nhiệt Grad-CAM để soi rõ xem máy tính đang nhìn vào đâu để đưa ra kết luận chẩn đoán.\n\n"
                "Về mặt kiểm nghiệm và ứng dụng thực tế: Chúng em mang mô hình đi kiểm tra trên một bộ ảnh của bệnh viện khác (tập dữ liệu ngoài Masoud Nickparvar) để chứng minh máy nhận biết chính xác người không có bệnh (độ đặc hiệu đạt 100%); và cuối cùng là đóng gói toàn bộ thành một phần mềm hoàn chỉnh chạy được trên máy tính bình thường, tự động đo đạc kích thước theo chuẩn quốc tế RECIST 1.1 và bấm một nút là xuất ngay ra phiếu kết quả bệnh án dạng PDF."
            )
        },
        {
            "num": 4,
            "title": "Slide 4: Bộ dữ liệu BRISC 2025 & Đường ống tiền xử lý tự động",
            "time": "2.0 phút",
            "screen": "Thông số BRISC 2025 (4,999 ảnh), Pipeline Skull Stripping + CLAHE, Hình 1 & Hình 2.",
            "speech": (
                "Kính thưa Thầy Cô, trên Slide 4 là dữ liệu nghiên cứu và quy trình tiền xử lý.\n\n"
                "Nghiên cứu sử dụng bộ dữ liệu chuẩn y tế BRISC 2025 gồm 4,999 ảnh lát cắt MRI sọ não chất lượng cao, bao quát cả 3 nhóm u: Glioma (1,621 ảnh), Meningioma (1,664 ảnh) và Pituitary (1,714 ảnh). Dữ liệu được chia độc lập thành tập Huấn luyện (80%), Kiểm định (6%) và tập Kiểm thử độc lập (14% tương đương 693 ảnh) với nhãn đa giác viền u chuẩn y khoa.\n\n"
                "Dữ liệu bao gồm các chuỗi xung cộng hưởng từ lâm sàng phổ biến:\n"
                "Chuỗi xung T1-weighted (T1W) và T1-weighted có tiêm thuốc đối quang từ (Gadolinium contrast enhancement - T1c).\n"
                "Đặc điểm hiển thị:\n"
                "- Nước và Dịch não tủy (CSF): Có màu TỐI (Đen).\n"
                "- Chất mỡ (Lipid): Có màu SÁNG (Trắng).\n"
                "- Chất trắng (White matter): Sáng hơn chất xám (vì bao myelin của chất trắng chứa nhiều chất béo).\n"
                "- Chất xám (Gray matter): Có màu xám sẫm hơn chất trắng.\n"
                "Mục đích lâm sàng: Cung cấp độ tương phản rất rõ giữa các cấu trúc giải phẫu bình thường của não, giúp bác sĩ nhìn rõ hình thái học, rãnh não và các thùy não.\n"
                "T1 có tiêm thuốc cản từ (T1-contrast / T1c): Khi tiêm thuốc đối quang từ (Gadolinium) vào mạch máu, tại những nơi có khối u phá vỡ hàng rào máu não (như U màng não Meningioma), thuốc sẽ ngấm vào mô u và làm vùng đó sáng rực lên, giúp định vị chính xác vị trí và vỏ u.\n\n"
                "Chuỗi xung T2-weighted (T2W) và FLAIR (Fluid Attenuated Inversion Recovery).\n"
                "Thể hiện đầy đủ 3 mặt phẳng giải phẫu không gian: Mặt cắt ngang (Axial), Mặt cắt trán (Coronal), và Mặt cắt đứng dọc (Sagittal).\n"
                "Đặc điểm hiển thị:\n"
                "- Nước và Dịch não tủy (CSF): Có màu SÁNG (Trắng rực).\n"
                "- Chất béo (Lipid): Tối hơn so với trên T1.\n"
                "- Chất trắng: Tối hơn chất xám.\n"
                "- Chất xám: Sáng hơn chất trắng.\n"
                "Mục đích lâm sàng: Đa số các tổn thương bệnh lý (viêm, xuất huyết cũ, khối u, phù nề tế bào) đều tích tụ nhiều nước. Do nước trên T2 có màu sáng, chuỗi xung T2 rất nhạy trong việc phát hiện các vùng bất thường và vùng phù nề quanh u (Edema).\n"
                "Đặc biệt với U tế bào thần kinh đệm (Glioma), khối u thâm nhiễm gây tích tụ dịch nhiều trong nhu mô não, ảnh T2 sẽ làm nổi bật toàn bộ phạm vi xâm lấn này.\n\n"
                "Chuỗi xung mở rộng liên quan: FLAIR (Fluid Attenuated Inversion Recovery):\n"
                "Trong các tập dữ liệu u não như BRISC, bạn cũng sẽ thấy ảnh FLAIR:\n"
                "Bản chất FLAIR là một chuỗi xung T2, nhưng máy chụp đã áp dụng một xung đảo ngược để triệt tiêu tín hiệu của dịch não tủy tự do (làm cho dịch trong các não thất biến thành màu đen giống T1).\n"
                "Nhờ vậy, vùng dịch não tủy bình thường không còn bị sáng chói lóa, giúp cho vùng u và vùng phù nề bệnh lý (vốn cũng có màu sáng) hiện lên cực kỳ nổi bật, không bị lẫn vào các khoang chứa dịch tự nhiên của não.\n\n"
                "Về đặc tính của 3 nhóm u não nghiên cứu:\n"
                "1. U tế bào thần kinh đệm (Glioma): Là khối u nội trục (intra-axial, tức là mọc từ ngay bên trong nhu mô não), phát sinh từ các tế bào nâng đỡ thần kinh. Glioma có đặc tính xâm lấn cao, ranh giới giữa khối u và mô não lành thường không sắc nét, kèm theo hiện tượng phù nề xung quanh (peritumoral edema). Khối u thường biểu hiện giảm tín hiệu trên T1W và tăng tín hiệu không đồng nhất trên T2/FLAIR. Việc khoanh vùng chính xác giúp bác sĩ phẫu thuật xác định mức độ thâm nhiễm vào vùng chức năng não.\n"
                "2. U màng não (Meningioma): Là khối u ngoài trục (extra-axial, tức là mọc ở lớp màng bao ngoài chứ không nằm trong ruột não), phát triển từ các tế bào màng nhện của màng não. Đa phần Meningioma là u lành tính, có bao xơ bọc rõ ràng và ranh giới rất tách bạch với vỏ não. Trên ảnh T1c, khối u ngấm thuốc đối quang từ rất mạnh và đồng nhất, kèm theo dấu hiệu đặc trưng là 'đuôi màng cứng' (Dural tail sign). Việc phân đoạn giúp đánh giá mức độ đè đẩy nhu mô não lân cận.\n"
                "3. U tuyến yên (Pituitary Adenoma): Là khối u phát sinh từ thùy trước tuyến yên, khu trú tại vị trí hố yên (sella turcica, một hõm xương nhỏ hình yên ngựa ở đáy sọ). Khối u ảnh hưởng trực tiếp đến trục nội tiết của cơ thể và có xu hướng phát triển vượt lên trên gây chèn ép giao thoa thị giác. Vị trí giải phẫu của u tuyến yên rất đặc thù, hoàn toàn khác biệt với vị trí của Glioma hay Meningioma.\n\n"
                "Đặc điểm thách thức lớn nhất thể hiện qua biểu đồ trực quan hóa dữ liệu:\n"
                "- Mất cân bằng diện tích cục bộ: Diện tích của vùng tổn thương chỉ chiếm trung bình từ 1.2% đến 6.8% tổng diện tích của lát cắt MRI. Phần diện tích còn lại (> 93%) hoàn toàn là nền đen và mô não bình thường. Nếu huấn luyện bằng các hàm mất mát thông thường (như Cross Entropy), mô hình sẽ có xu hướng tối ưu hóa bằng cách dự đoán tất cả các pixel là nền não lành.\n"
                "- Mất cân bằng giữa các lớp: Số lượng mẫu và hình thái của Meningioma có độ tương phản cao, dễ học hơn so với sự biến thiên phức tạp về kích thước và hình dạng của Glioma.\n\n"
                "Để chuẩn hóa chất lượng ảnh đầu vào, chúng em xây dựng quy trình tiền xử lý 2 giai đoạn tự động:\n"
                "Giai đoạn 1 là Bóc tách hộp sọ (Skull Stripping): sử dụng phân ngưỡng Otsu kết hợp biến đổi hình thái học và thuật toán trích xuất thành phần liên thông lớn nhất (LCC). Bước này giúp loại bỏ trọn vẹn lớp xương sọ và màng cứng có cường độ sáng cao, triệt tiêu nguy cơ báo động dương tính giả.\n"
                "Giai đoạn 2 là Cân bằng tương phản thích ứng cục bộ (CLAHE): thiết lập Clip Limit = 2.0 trên lưới 8x8, giúp nâng cao độ tương phản giữa bờ viền khối u và nhu mô não xung quanh mà không làm khuếch đại nhiễu nền."
            )
        },
        {
            "num": 5,
            "title": "Slide 5: Chiến lược kiến trúc đa trường phái (Cascaded Pipeline)",
            "time": "1.5 phút",
            "screen": "So sánh Phân đoạn thực thể vs Phân đoạn ngữ nghĩa, Quy trình hợp tác liên hoàn 2 chặng.",
            "speech": (
                "Một câu hỏi quan trọng được đặt ra là: Tại sao đề tài lại dùng cùng lúc cả hai trường phái mạng học sâu khác nhau?\n\n"
                "Lý do là hai trường phái này bổ trợ cho nhau như một cặp bài trùng:\n"
                "Trường phái thứ nhất là Phân đoạn thực thể (Instance Segmentation, tiêu biểu là YOLOv8 và YOLO11). Ưu điểm số một của nó là cực kỳ nhanh, đạt tới 36 đến 38 hình trên một giây (tức là chỉ mất khoảng 15 phần nghìn giây cho một bức ảnh). Nó giống như một người lính gác cổng, quét thật nhanh qua 100 lát cắt não để phát hiện ngay xem lát cắt nào có khối u và khoanh một chiếc khung chữ nhật xung quanh vị trí u.\n\n"
                "Trường phái thứ hai là Phân đoạn ngữ nghĩa (Semantic Segmentation, tiêu biểu là U-Net và SegFormer). Nó giống như một chuyên gia soi kính hiển vi, chạy chậm hơn một chút nhưng lại soi kỹ từng điểm ảnh li ti để gọt tỉa chính xác từng khúc lồi lõm của ranh giới u, giúp đo đúng thể tích thực tế.\n\n"
                "Từ đó, chúng em kết hợp thành 'Quy trình hợp tác hai chặng liên hoàn' (Cascaded Pipeline): Bước 1, cho YOLO quét siêu tốc để phát hiện vùng nghi ngờ (ROI). Bước 2, tự động cắt riêng vùng nghi ngờ đó chuyển sang cho U-Net hoặc SegFormer gọt giũa đường viền chi tiết và đo đạc kích thước. Nhờ vậy, hệ thống vừa đạt tốc độ tức thì, vừa đạt độ chính xác vi mô."
            )
        },
        {
            "num": 6,
            "title": "Slide 6: Kiến trúc phân đoạn thực thể YOLO-seg (Anchor-Free)",
            "time": "1.0 phút",
            "screen": "Sơ đồ kiến trúc YOLO-seg, C2f/C3k2, Proto-net 32 mặt nạ 160x160 (Hình 3).",
            "speech": (
                "Trên Slide 6 là sơ đồ chi tiết của mô hình quét nhanh YOLO-seg.\n\n"
                "Điểm cải tiến lớn nhất ở đây là cơ chế Anchor-free (tức là không dùng các khung hộp mẫu cố định). Trước đây, các mô hình cũ bắt buộc phải ướm các khung hình chữ nhật có sẵn lên khối u, nhưng vì u não có hình thù méo mó ngẫu nhiên nên rất hay bị lệch. Cơ chế Anchor-free cho phép máy tính tự đo trực tiếp khoảng cách từ tâm khối u ra 4 phía, nên bắt trúng khối u rất nhanh và linh hoạt.\n\n"
                "Mô hình sử dụng mạng trích xuất đặc trưng đời mới C2f trên YOLOv8 và C3k2 trên YOLO11.\n\n"
                "Đặc biệt, nhánh Proto-net (mạng sinh mặt nạ nguyên mẫu) sẽ tạo sẵn 32 bức ảnh mặt nạ khuôn mẫu cơ bản. Cùng lúc đó, đầu phát hiện tính ra 32 con số hệ số tương ứng. Chỉ cần lấy 32 con số này nhân với 32 mặt nạ khuôn mẫu là ngay lập tức vẽ ra được đường viền khối u trong một thao tác duy nhất, đó là lý do vì sao YOLO có thể chạy với tốc độ siêu tốc."
            )
        },
        {
            "num": 7,
            "title": "Slide 7: Kiến trúc Attention U-Net & Vision Transformer phân cấp",
            "time": "1.0 phút",
            "screen": "Kiến trúc Attention U-Net + scSE, ResNeXt50-UNet++, SegFormer (Hình 4).",
            "speech": (
                "Chuyển sang nhóm mô hình gọt viền chi tiết trên Slide 7, chúng em triển khai 3 kiến trúc tiên tiến:\n\n"
                "Thứ nhất là Attention U-Net: sử dụng bộ khung EfficientNet-B0 rất nhẹ (chỉ 6.4 triệu tham số) giúp máy tính văn phòng chạy mượt mà và không bị 'học vẹt'. Tại các đường liên kết tắt (Skip Connection - tức là đường truyền thẳng chi tiết từ ảnh gốc sang kết quả), chúng em gắn thêm bộ chú ý kép scSE. Bộ này hoạt động như một kính lọc: vừa soi xem u nằm ở tọa độ không gian nào, vừa chọn lọc các lớp màu sắc quan trọng của bệnh lý u.\n\n"
                "Thứ hai là ResNeXt50-UNet++: có các đường dẫn giải mã đan xen chằng chịt như lưới nhện (Dense Skip Pathways), giúp giữ lại tối đa các chi tiết giải phẫu nhỏ bé không bị mất mát.\n\n"
                "Thứ ba là SegFormer (MiT-B2): đại diện cho trường phái Vision Transformer đời mới. Khác với các mạng truyền thống chỉ nhìn được một vùng cục bộ nhỏ hẹp, SegFormer có cơ chế chú ý toàn cục (Self-Attention), cho phép máy tính nhìn bao quát toàn bộ hai bán cầu não cùng một lúc để so sánh sự đối xứng, giúp phát hiện rất sớm các khối u thâm nhiễm mờ nhạt."
            )
        },
        {
            "num": 8,
            "title": "Slide 8: Đột phá hàm mất mát Boundary Loss (SDF)",
            "time": "1.5 phút",
            "screen": "Toán học Signed Distance Maps, công thức Boundary Loss, kết quả giảm 26% HD95, 35% ASSD.",
            "speech": (
                "Kính thưa Thầy Cô, một trong những đóng góp học thuật cốt lõi nhất của đề tài là việc ứng dụng hàm mất mát biên độ Boundary Loss.\n\n"
                "Như em đã trình bày ở phần đặt vấn đề: nếu dùng công thức tính điểm Dice thông thường, máy tính chỉ đếm xem diện tích hai vùng có đè lên nhau nhiều hay không. Khi khối u to, việc mô hình vẽ lẹm ra ngoài hoặc hụt vào trong vài milimet ở bờ viền chỉ chiếm một tỉ lệ phần trăm rất nhỏ về diện tích, nên máy tính không coi đó là lỗi nặng và có xu hướng làm tròn vo bờ u (Over-smoothing).\n\n"
                "Để trị dứt điểm lỗi này, chúng em đưa vào thuật toán 'Bản đồ khoảng cách dấu' (Signed Distance Maps - SDF). Thuật toán này sẽ đo khoảng cách thực tế (tính bằng milimet) từ từng điểm ảnh đến đường viền chuẩn của bác sĩ: nếu điểm đó nằm ngoài khối u thì khoảng cách mang dấu dương, nằm trong u thì mang dấu âm, và nằm ngay trên đường viền thì bằng 0. Hàm Boundary Loss sẽ lấy khoảng cách này để phạt điểm: mô hình vẽ sai càng xa đường viền thực tế thì bị phạt trừ điểm càng nặng.\n\n"
                "Chúng em phối hợp công thức hỗn hợp gồm: 40% Dice Loss (để giữ diện tích), 40% Focal Loss (để bớt chú ý vào nền não lành) và 20% Boundary Loss (để ép chặt ranh giới viền). Kết quả thực nghiệm vượt ngoài mong đợi: sai số khoảng cách Hausdorff 95% (HD95 - tức là khoảng cách lệch lớn nhất của đường viền) giảm mạnh từ 9.45 mm xuống chỉ còn 6.99 mm (giảm tới 26.0%), giúp bờ viền khối u được khôi phục sắc nét và an toàn cho phẫu thuật."
            )
        },
        {
            "num": 9,
            "title": "Slide 9: Bảng đối chuẩn hiệu năng toàn diện trên tập kiểm thử BRISC 2025",
            "time": "1.5 phút",
            "screen": "Bảng tổng hợp 6 mô hình với 7 chỉ số (Dice, IoU, HD95, ASSD, FPS, Params) & Biểu đồ Hình 5.",
            "speech": (
                "Trên Slide 9 là bảng so sánh đối đầu toàn diện của cả 6 mô hình trên tập kiểm thử gồm 693 ảnh của bộ dữ liệu BRISC 2025.\n\n"
                "Nhìn vào bảng số liệu, quý Thầy Cô có thể thấy rõ thế mạnh riêng của từng trường phái:\n"
                "Về tốc độ: Nhóm YOLO thắng tuyệt đối. YOLO11s-seg đạt 38.1 khung hình/giây trên chip CPU bình thường với dung lượng rất nhẹ chỉ 9.4 triệu tham số, chạy nhanh gấp gần 10 lần các mô hình U-Net.\n\n"
                "Về độ phủ diện tích: Mô hình SegFormer dẫn đầu về chỉ số tương đồng Dice đạt 83.00%. Mô hình ResNeXt50-UNet++ dẫn đầu về chỉ số diện tích giao nhau IoU đạt 74.60%.\n\n"
                "Đặc biệt, về độ sắc nét của đường viền: Mô hình Boundary-Aware U-Net giữ ngôi vị quán quân với sai số khoảng cách HD95 thấp nhất (chỉ 6.99 mm, giảm 26.0%) và sai số bề mặt ASSD chỉ 4.65 mm (cải thiện 35.1%).\n\n"
                "Điều này chứng minh rằng không có một mô hình nào là 'vạn năng' cho mọi tiêu chí, mà mỗi mô hình nắm giữ một mắt xích quan trọng trong quy trình chẩn đoán."
            )
        },
        {
            "num": 10,
            "title": "Slide 10: Bóc tách hiệu năng phân đoạn theo từng nhóm mô bệnh học",
            "time": "1.5 phút",
            "screen": "3 cột phân tích: U màng não (90-92%), U tuyến yên (88-90%), U thần kinh đệm (81-86%).",
            "speech": (
                "Khi bóc tách kết quả chi tiết theo từng loại bệnh u não trên Slide 10, kết quả của máy tính khớp hoàn toàn với lý thuyết y khoa lâm sàng:\n\n"
                "Thứ nhất, nhóm U màng não (Meningioma) đạt điểm số cao nhất ở tất cả các mô hình, với điểm Dice từ 90.6% đến 92.9% và sai số đường viền rất thấp chỉ khoảng 5 mm. Lý do là vì u màng não nằm ở phía ngoài, có vỏ xơ bọc rõ ràng nên máy tính nhận dạng rất dễ dàng.\n\n"
                "Thứ hai, nhóm U tuyến yên (Pituitary) đạt độ chính xác rất ổn định trên 90% (Dice đạt 90.64% trên SegFormer) vì khối u nằm cố định ở một vị trí giải phẫu đặc thù là đáy sọ hố yên, ít bị chạy lung tung qua các lát cắt.\n\n"
                "Thứ ba, nhóm U thần kinh đệm (Glioma) là thử thách khó khăn nhất. Vì đây là u ác tính ăn lan, thâm nhiễm chân rết vào các sợi thần kinh nên điểm số chung chỉ dao động từ 81.5% đến 86.6%. Ở nhóm bệnh hiểm nghèo này, mô hình SegFormer thể hiện ưu thế vượt trội nhất (Dice đạt 86.66%) vì nó có tầm nhìn bao quát toàn bộ não, giúp phát hiện được cả những vùng tế bào u thâm nhiễm mờ nhạt nhất."
            )
        },
        {
            "num": 11,
            "title": "Slide 11: Kiểm định độc lập ngoại kiểm trên bộ dữ liệu Masoud Nickparvar",
            "time": "1.5 phút",
            "screen": "Lưới ảnh đối chuẩn 4 ca bệnh ngoại kiểm (No Tumor, Meningioma, Pituitary, Glioma) và nhận xét.",
            "speech": (
                "Kính thưa Thầy Cô, để đảm bảo máy tính không bị tật 'học vẹt' (tức là chỉ đoán giỏi trên tập ảnh cũ, gặp ảnh của bệnh viện khác thì đoán sai), chúng em đã tiến hành kiểm tra trên một bộ dữ liệu hoàn toàn xa lạ là Masoud Nickparvar.\n\n"
                "Kết quả thực nghiệm trên Slide 11 cho thấy:\n"
                "Hàng trên cùng là ca Não hoàn toàn khỏe mạnh (No Tumor): Cả 6 mô hình đều đồng loạt đưa ra kết luận là 0 pixel khối u, đạt độ chính xác tuyệt đối 100%. Điều này chứng minh thuật toán bóc tách hộp sọ đã hoạt động rất hiệu quả, máy không hề bị nhìn nhầm xương sọ hay các nếp gấp não bình thường thành khối u (không có dương tính giả).\n\n"
                "Ở 3 ca bệnh có u tiếp theo: Cả 6 mô hình đều đồng thuận chỉ đúng vị trí u màng não và u tuyến yên. Riêng với ca U thần kinh đệm phức tạp ở hàng cuối cùng: mô hình YOLO11s nhận diện độ tin cậy 87%, SegFormer vẽ bao quát toàn bộ vùng chân u ăn lan (chiếm 7.44% diện tích não), còn Boundary U-Net bám chặt lấy vùng lõi khối u (3.06%), cho bác sĩ một cái nhìn đa chiều rất rõ ràng."
            )
        },
        {
            "num": 12,
            "title": "Slide 12: Minh bạch hóa trọng số ra quyết định với Grad-CAM (XAI)",
            "time": "1.5 phút",
            "screen": "Nguyên lý Grad-CAM trên Decoder và giải thích sinh học vì sao nhiệt bôi vào mỏm viền u Glioma.",
            "speech": (
                "Để bác sĩ thực sự tin tưởng và sử dụng trí tuệ nhân tạo, mô hình không thể là một 'chiếc hộp đen' bí ẩn. Trên Slide 12, chúng em ứng dụng kỹ thuật Grad-CAM để vẽ ra một 'bản đồ nhiệt' (vùng màu đỏ/vàng thể hiện nơi mà máy tính đang tập trung nhìn nhiều nhất để đưa ra quyết định).\n\n"
                "Có một điểm rất thú vị: Trên ảnh u Glioma ác tính, bản đồ nhiệt không hề tô đỏ đều hết toàn bộ khối u, mà chỉ tập trung sáng rực vào hai chiếc 'mỏm viền' ở cực trên của tổn thương.\n\n"
                "Hiện tượng này hoàn toàn khớp với bản chất y khoa: Vùng lõi ở chính giữa của khối u Glioma thực chất là mô đã chết (gọi là mô hoại tử trung tâm, Central Necrosis), các tế bào ở đây không còn hoạt động nên máy tính không chú ý. Ngược lại, vùng mỏm viền bên ngoài (Enhancing Rim) mới là nơi các tế bào ung thư đang phân chia mạnh mẽ, hút nhiều máu nuôi và hung hãn ăn lan vào não lành nhất. Việc máy tính tự động dồn điểm nhìn vào đúng hai mỏm viền này chứng minh mạng nơ-ron thực sự học được bản chất bệnh lý của khối u, chứ không phải đoán mò theo các chi tiết ngẫu nhiên ở nền ảnh."
            )
        },
        {
            "num": 13,
            "title": "Slide 13: Module đo đạc hình thái học chuẩn quốc tế RECIST 1.1",
            "time": "1.0 phút",
            "screen": "Bảng danh mục 6 thông số vật lý RECIST 1.1 (D_max, D_min, Area, Perimeter, Brain Occupancy, Volume).",
            "speech": (
                "Sau khi vẽ được đường viền khối u, bài toán thực tế tiếp theo là phải đo đạc kích thước thật ngoài đời để bác sĩ theo dõi phác đồ điều trị. Trên Slide 13 là module đo đạc tự động theo tiêu chuẩn quốc tế RECIST 1.1.\n\n"
                "Dựa vào thông số kích thước vật lý của từng điểm ảnh (Pixel Spacing, tính bằng milimet) và độ dày của lát cắt (Slice Thickness), hệ thống tự động tính ra 6 chỉ số y khoa quan trọng:\n"
                "1. Đường kính lớn nhất (D_max, tính bằng mm): là đoạn thẳng nối 2 điểm xa nhất trên khối u. Đây là chỉ số quan trọng nhất để xem sau khi hóa trị hay xạ trị khối u có teo nhỏ lại hay không;\n"
                "2. Đường kính ngắn nhất vuông góc (D_min, tính bằng mm) theo chuẩn của Tổ chức Y tế Thế giới (WHO);\n"
                "3. Diện tích mặt cắt của khối u (tính bằng mm²);\n"
                "4. Chu vi đường bao quanh khối u (mm), phản ánh mức độ gồ ghề của bờ u;\n"
                "5. Tỉ lệ chiếm thể tích nhu mô não (tính bằng %), cho biết khối u đã chiếm bao nhiêu phần trăm thể tích của hộp sọ não;\n"
                "6. Thể tích khối u ước tính (tính bằng centimet khối - cm³), hỗ trợ bác sĩ lên kế hoạch liều lượng chiếu xạ chính xác."
            )
        },
        {
            "num": 14,
            "title": "Slide 14: Hệ thống hỗ trợ chẩn đoán CADx & Xuất bệnh án PDF tự động",
            "time": "1.5 phút",
            "screen": "Giao diện web Streamlit NeuroScan CADx, tối ưu CPU, chế độ Second-Opinion, sinh PDF (Hình 6).",
            "speech": (
                "Để đưa các thuật toán trên giấy thành phần mềm thực tế trong tay bác sĩ, chúng em đã đóng gói toàn bộ thành ứng dụng web mang tên NeuroScan CADx trên Slide 14.\n\n"
                "Hệ thống có 3 điểm nổi bật phục vụ trực tiếp cho bệnh viện:\n"
                "Thứ nhất là Chạy mượt mà trên máy tính CPU văn phòng thông thường: không bắt buộc bệnh viện tuyến huyện hay phòng khám cơ sở phải mua sắm máy chủ hay card đồ họa (GPU) đắt tiền hàng trăm triệu đồng.\n"
                "Thứ hai là Chế độ Hội chẩn đa mô hình (Second-Opinion Mode, tức là chế độ bác sĩ thứ hai): cho phép hiển thị song song kết quả của cả 6 mô hình trên cùng một màn hình để bác sĩ tiện so sánh, đối chiếu góc nhìn và xem bản đồ nhiệt Grad-CAM.\n"
                "Thứ ba là Tự động xuất phiếu kết quả y khoa dạng PDF: bác sĩ chỉ cần bấm một nút, phần mềm sẽ tự động tổng hợp thông tin bệnh nhân, ảnh gốc, ảnh khoanh viền khối u, bản đồ nhiệt giải thích và toàn bộ bảng số liệu kích thước RECIST 1.1 thành một trang bệnh án PDF chuẩn mực, sẵn sàng in ra giấy hoặc lưu vào bệnh án điện tử (EMR)."
            )
        },
        {
            "num": 15,
            "title": "Slide 15: Thảo luận học thuật, hạn chế đề tài & Hướng phát triển",
            "time": "1.0 phút",
            "screen": "Thảo luận sự đánh đổi diện tích vs biên độ, hạn chế 2D, kế hoạch 3D Swin UNETR và Multimodal.",
            "speech": (
                "Kính thưa Hội đồng, từ các kết quả thực nghiệm, chúng em rút ra bài học kinh nghiệm rất quý giá: Trong bài toán phân đoạn ảnh y tế, điểm diện tích Dice cao không đồng nghĩa với việc đã an toàn cho bệnh nhân. Việc ứng dụng Boundary Loss để kéo giảm 26% sai số khoảng cách đường viền có ý nghĩa thực tế hơn rất nhiều so với việc cố gắng cày cuốc để tăng thêm một vài phần trăm diện tích trùng khớp.\n\n"
                "Về mặt hạn chế: Hiện tại mô hình mới chỉ xử lý trên từng lát cắt phẳng 2 chiều (2D) riêng lẻ, chưa ghép các lát cắt liền kề lại để nhìn thành một khối không gian 3 chiều liên tục.\n\n"
                "Trong tương lai, chúng em sẽ mở rộng đề tài theo 3 hướng:\n"
                "1. Nâng cấp lên mô hình 3D (như kiến trúc 3D Swin-UNETR) để dựng hình khối 3 chiều hoàn chỉnh, phục vụ cho phẫu thuật có robot dẫn đường;\n"
                "2. Kết hợp đồng thời cả 4 chế độ chụp MRI (T1, T1 có thuốc cản từ, T2 và FLAIR) để bóc tách rõ từng phần: lõi u, vỏ u và vùng phù nề;\n"
                "3. Tích hợp mô hình ngôn ngữ lớn y khoa (Medical AI) để máy tính tự động viết thành đoạn văn nhận xét kết luận bệnh án bằng tiếng Việt một cách tự nhiên."
            )
        },
        {
            "num": 16,
            "title": "Slide 16: Kết luận & Lời cảm ơn (Q&A)",
            "time": "1.0 phút",
            "screen": "Tóm tắt 3 kết luận chính, lời cảm ơn Hội đồng, chuyển sang phiên Hỏi & Đáp.",
            "speech": (
                "Để kết thúc bài báo cáo, em xin tóm tắt lại 3 kết quả lớn nhất mà đề tài đã đạt được:\n\n"
                "Một là, thử nghiệm và đối chuẩn thành công 6 mô hình trí tuệ nhân tạo trên tập BRISC 2025 và kiểm tra chéo trên tập Masoud Nickparvar, tạo ra sự phối hợp hiệu quả giữa mô hình quét siêu tốc YOLO và mô hình gọt viền tỉ mỉ U-Net/SegFormer.\n\n"
                "Hai là, chứng minh hiệu quả vượt trội của hàm Boundary Loss trong việc xóa bỏ tật làm tròn bờ viền, giảm 26% sai số ranh giới u; kết hợp bản đồ nhiệt Grad-CAM giúp bác sĩ hiểu rõ lý do máy tính đưa ra quyết định.\n\n"
                "Ba là, hoàn thiện phần mềm NeuroScan CADx gọn nhẹ trên máy tính thường, tự động đo đạc theo chuẩn quốc tế RECIST 1.1 và bấm nút xuất ngay ra phiếu kết quả bệnh án PDF.\n\n"
                "Em xin trân trọng gửi lời cảm ơn sâu sắc đến Thầy Hoàng Văn Quý đã tận tình hướng dẫn, chỉ bảo em trong suốt quá trình thực hiện đề tài. Em cũng xin chân thành cảm ơn quý Thầy Cô trong Hội đồng đã dành thời gian quý báu lắng nghe bài báo cáo của em. Em xin phép được lắng nghe những ý kiến đóng góp quý báu và sẵn sàng giải đáp các câu hỏi của quý Thầy Cô. Em xin trân trọng cảm ơn!"
            )
        }
    ]

    for item in slides_content:
        p_h = doc.add_paragraph()
        p_h.paragraph_format.space_before = Pt(14)
        p_h.paragraph_format.space_after = Pt(2)
        r_h = p_h.add_run(f"■ {item['title']} (Thời lượng: ~{item['time']})")
        r_h.font.name = "Times New Roman"
        r_h.font.size = Pt(12)
        r_h.font.bold = True
        r_h.font.color.rgb = RGBColor(30, 58, 138)

        p_scr = doc.add_paragraph()
        p_scr.paragraph_format.space_after = Pt(4)
        r_sc = p_scr.add_run(f"Nội dung trên màn hình: {item['screen']}")
        r_sc.font.name = "Times New Roman"
        r_sc.font.size = Pt(9.5)
        r_sc.font.italic = True
        r_sc.font.color.rgb = RGBColor(100, 100, 100)

        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_after = Pt(10)
        p_sp.paragraph_format.line_spacing = 1.25
        r_sp = p_sp.add_run("Lời trình bày trực tiếp:\n" + item['speech'])
        r_sp.font.name = "Times New Roman"
        r_sp.font.size = Pt(11)
        r_sp.font.color.rgb = RGBColor(15, 23, 42)

        p_d = doc.add_paragraph()
        p_d.paragraph_format.space_after = Pt(8)
        r_d = p_d.add_run("―" * 55)
        r_d.font.color.rgb = RGBColor(220, 220, 220)

    out_path = r"d:\Học Sâu và Ứng dụng\Tumor\docs\Kich_Ban_Thuyet_Trinh_Springer_Nature.docx"
    doc.save(out_path)
    print(f"Updated successfully to: {out_path}")

if __name__ == '__main__':
    create_friendly_script_docx()
