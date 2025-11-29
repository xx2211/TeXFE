from rapid_latex_ocr import LaTeXOCR

print("正在强制触发模型下载...")
# 初始化时，库会自动检测本地有没有模型
# 如果没有，它会自动从它内置的、肯定正确的地址下载
model = LaTeXOCR()

print("下载完成！")
