import getpass  #隐藏输入
import hashlib  #转换加密

#输入隐藏
pwd = getpass.getpass("PW:")   #输入密码不显示
print(pwd)

#hash对象
# hash = hashlib.md5()  #生成对象

#算法加盐(#$awv3_)
hash = hashlib.md5("*#$awv3_".encode())
hash.update(pwd.encode())  #算法加密
pwd = hash.hexdigest()  #提取加密后的密码
print(pwd)
#注：　adc123#$awv3_   　#后台算法加盐。　钓鱼网站：中途截获密码，或在基站网络设备截获。





















