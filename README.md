# auto_ipa
iOS 自动打包工具  基于python3 请自行安装python3, 需要安装一个biplist的包 <br>
fir上传测试包, altool上传正式包到itunes, 
<br>安装fir.im 执行gem install fir-cli,
<br> altool 为loader的一个工具在loader下显示包内容 在framework路径大概为/Applications/Xcode.app/Contents/Applications/Application\ Loader.app/Contents/Frameworks/ITunesSoftwareService.framework/Versions/A/Support/altool

<br>configure.plist是配置文件, 需要配置

<br>development.plist 为测试包的配置
<br>product.plist 为生产包的配置 
<br>以上两个配置信息, 如果不知道如何填写,  可自行打对应的包 ExportOptions.plist重命名替换即可

<br>ipa文件夹为产生ipa的地址
<br>xcarchive为产生xcarchive的地址




