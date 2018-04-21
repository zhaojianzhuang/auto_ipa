#!/usr/env/bin python
# -*- coding: utf-8 -*- 
import os
import sys
import time
import hashlib
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
from biplist import *
import collections 

# build 一个以时间为名字为app的名字, 一个为xcarchive路径
BuildPaths = collections.namedtuple('BuildPaths', ['app_name', 'archive_xcarchivePath'])

# ipa存的所在目录
app_path = os.getcwd() + '/ipa'
# archive之后的xcarchive
app_xcarchive = os.getcwd() + '/xcarchive'

configure = readPlist(os.path.join(os.getcwd(), 'configure.plist'))
# 项目根目录
project_path = configure['project_path']
# firm的api token
fir_api_token = configure['fir_api_token']
#项目的名字
project = configure['project']
# 发送人的邮箱地址
from_addr = configure['from_addr']
# 邮箱配置的token
password = configure['password']
# 邮件server
smtp_server = configure['smtp_server']
# 发送人的邮件
to_addr = configure['to_addr']
# app账号
app_username = configure['app_username']
# app账号的密码
app_password = configure['app_password']

# 清理项目 创建build目录
def clean_project_mkdir_build():
    os.system('cd %s;xcodebuild clean' % project_path) # clean 项目

# archive项目 xcarchive 放在xcarchive目录下
def build_project():
    app_name = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
    os.system ('cd %s;xcodebuild -list'%project_path)
    scheme = input('write which scheme do you want to archive\n')
    archive_xcarchivePath = app_xcarchive + '/' + project + app_name + '.xcarchive'
    os.system ('cd %s;xcodebuild archive -workspace %s.xcworkspace -scheme %s -configuration release  -archivePath %s ONLY_ACTIVE_ARCH=NO || exit'%(project_path,project, scheme, archive_xcarchivePath))
    return BuildPaths(app_name, archive_xcarchivePath)

# 转换为ipa放在ipa目录下
def build_ipa(isDev, build_path):
    plist_path = '/development.plist'
    if not isDev:
        plist_path = '/product.plist' 

    if not os.path.exists(f'{app_path}/{build_path.app_name}'):
        os.makedirs(f'{app_path}/{build_path.app_name}')

    os.system('xcodebuild -exportArchive -archivePath %s -exportPath %s -exportOptionsPlist %s'%(build_path.archive_xcarchivePath, os.getcwd() + '/ipa/' + build_path.app_name + '/', os.getcwd() + plist_path))
  
   
    

#上传到fir 
def upload_fir(app_name):
    try:
        path = get_ipapath(app_name)
        # 直接使用fir 有问题 这里使用了绝对地址 在终端通过 which fir 获得
        result = os.system("/usr/local/bin/fir p '%s' -T '%s'" % (ipaPath,fir_api_token))
        if result != 0:
            return False
        return True
    except FileNotFoundError as e:
        print(e)
    return False   

# 上传到appstore
def upload_appstore(app_name):
    try:
        altool = '/Applications/Xcode.app/Contents/Applications/Application\ Loader.app/Contents/Frameworks/ITunesSoftwareService.framework/Versions/A/Support/altool'
        path = get_ipapath(app_name)
        print('正在检测是否合法...')
        command = f'{altool} -v -f {path} -u {app_username} -p {app_password} -t ios'
        result = os.system(command)
        if result != 0:
            return False
        print('正在上传...')
        command = f'{altool} --upload-app -f \"{path}\" -u {app_username} -p {app_password}'
        print(command)
        result = os.system(command)
        if result != 0:
            return False
        return True
    except FileNotFoundError as e:
        print(e)  

#  获取到ipa的路径  
def get_ipapath(app_name):
    if os.path.exists("%s/%s" % (app_path,app_name)):
        for parent, dirnames, fileNames in os.walk(app_path + '/' + app_name):
            for fileName in fileNames:
                if fileName.endswith('.ipa'):
                    print(fileName)
                    ipaPath = app_path + '/' + app_name + '/' + fileName 
                    return ipaPath
    
        raise FileNotFoundError


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

# 发邮件
def send_mail(changelog, archiveXcarchivePath, isDev):
    
    plist = readPlist(archiveXcarchivePath + '/Info.plist')
    version = plist['ApplicationProperties']['CFBundleShortVersionString']
    msg = MIMEText('iOS正式项目已经打包完毕，请前往 itunes 查看！\n change log:%s'%changelog, 'plain', 'utf-8')
    if isDev :
        msg = MIMEText('iOS测试项目已经打包完毕，请前往 http://fir.im/hlyzdriverdev  下载测试！\n change log:%s'%changelog, 'plain', 'utf-8')
    msg['From'] = _format_addr(' <%s>' % from_addr)
    msg['To'] = _format_addr('<%s>' % to_addr)
    
    msgtitle = 'iOS%s转测'%version
    msg['Subject'] = Header(msgtitle, 'utf-8').encode()
    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()

def main():
    # 输入正式或者测试, 正式直接上传到itunes  测试到fir
    str = input('input 1 is product 0 is dev\n')
    isDev = True
    if str == '1':
        isDev = False
    # 写changelog
    changelog = input('write change log:\n')
    # 清理并创建build目录
    clean_project_mkdir_build()
    # 编译coocaPods项目文件并 执行编译目录
    build_path = build_project()
    # 打包ipa 并制定到桌面
    build_ipa(False, build_path)
    if isDev:
        if upload_fir(build_path.app_name):
            print('已经上传到了fir')
            send_mail(changelog, build_path.archive_xcarchivePath, isDev)
    else:
        if upload_appstore(build_path.app_name):
            print('已经上传到了itunes ')
            send_mail(changelog, build_path.archive_xcarchivePath, isDev)
               
if __name__ == '__main__':
    main()
