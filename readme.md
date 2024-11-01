# 华电在线刷视频课程bot

## !!!!! 免责声明: 使用本脚本产生的任何后果自负.

### 使用方法
1. 登录华电在线, 找到课程, 进入课程页面, 复制课程第一节url, 比如:

http://school.huadianline.com/course/watch/193_12792.html

复制课程最后一节url 比如:

http://school.huadianline.com/course/watch/193_12822.html
其中, 193 是**课程ID**, 12792, 12822 是**视频ID**.

2. 脚本使用方法:

安装python

安装requests包, pip install requests

安装ffmpeg(部分视频需要下载后获取时长)

运行:

python bot.py 登录用户名 登录用户密码 课程ID 视频ID