## TexFE - 公式识别工具

基于rapid-latex-ocr的离线公式识别工具，Mathpix的开源替代方案。支持windows截图识别以及手机拍照联动。

#### 为什么选择TexFE

* 完全免费开源：告别昂贵的订阅费。
* 离线识别：无需联网，保护隐私，速度极快。
* 手机PC无缝联动：独家功能！手机拍公式，电脑直接出代码。

#### 主要技术栈

* rapid-latex-ocr
* qt

#### 主要功能：
1. 截取屏幕区域识别公式
2. 手机扫码上传图片,电脑端编辑选取区域识别公式
3. 编辑、预览识别结果

#### 环境

操作系统:     windows11
  (linux或其他版本的windows系统可自行测试)

python环境:  python3.10 64位

#### 通过可执行文件运行
1. 下载  [release](https://github.com/xx2211/TeXFE/releases) 中的压缩包TeXFE-vx.xx.zip
2. 解压后双击 TeXFE.exe即可运行
3. 启动后可以通过 1)托盘图标 或 2)快捷键alt+q、alt+m识别公式


#### 通过python源码运行
1. 执行``克隆项目到本地, 然后执行`cd TeXFE`进入项目目录
2. 执行 `pip install -r requirements.txt` 安装依赖
3. 执行 `python main.py` 启动程序
4. 启动后可以通过 1)托盘图标 或 2)快捷键alt+q、alt+m识别公式

#### 通过python源码打包

1. 执行 `pip install -r requirements.txt` 安装项运行所需依赖
2. 执行 `pip install requests onnx` 安装打包所需依赖
3. 执行 `pip install pyinstaller` 安装打包工具
4. 执行 `pyinstaller TeXFE.spec` 进行打包
5. 打包生成的文件在dist目录下


