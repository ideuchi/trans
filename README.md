# 翻訳支援コマンドツール(trans)

「trans」はテキスト／ファイル／ディレクトリを翻訳するバッチ翻訳ツールです。  
翻訳したいデータが多めで、無料翻訳サイトに何度もコピー＆ペーストを繰り返すのは面倒、という場合に役立ちます。  
ファイル／ディレクトリを翻訳する場合、テキストファイルだけでなく、HTMLやOffice形式、PDFも翻訳対象となります。

"trans" is batch translation tool for translating text/file/directory.  
This is useful if you have much data to translate and you don't want to copy and paste many times into a free translation site.  
When translating file/directory, not only text files but also HTML, Office formats, and PDFs are also translated.


## 事前準備(Prerequisites)

Windowsの場合は、Linuxコマンドを実行するための環境が必要です。（WSL(Windows Subsystem for Linux)等）  
また、コマンドを実行するために以下のパッケージが必要です。

For Windows, an evironment for execute linux command is necessary. ex. install WSL (Windows Subsystem for Linux), etc.  
In addition, the following packages are required to execute the command.

~~~~
Linux package
  curl
  openssl
  python (>= 3.6)

Python package
  requests_oauthlib
  requests
~~~~

「みんなの自動翻訳@TexTra」のサービスを利用する場合、ユーザー登録が必要です。  
（他のサービスと連携する場合は、必要に応じてリクエスト先等を変更してください。）

You need to register to use the "みんなの自動翻訳@TexTra" service, you need to register yourself.  
(If you want to collaborate with other services, please change the request address, etc.)


## インストール方法(Installation)

以下のコマンドを実行してください。

Execute command below.

```sh
$ git clone https://github.com/ideuchi/trans
```


## 設定方法(Setup)

API設定ファイルを編集します。

Edit the setting file of API.

```sh
$ cd trans
$ vi APIInfo.ini
```

編集前(before editing)：
~~~~
# (required) account information for API
name=                                            # input your account name
key=                                             # input your API key
secret=                                          # input your API secret
=====snip=====
↓
編集後(after editing)：
# (required) account information for API
name=YOUR_NAME                                   # input your account name
key=YOUR_KEY                                     # input your API key
secret=YOUR_SECRET                               # input your API secret
=====snip=====
~~~~


## 使い方(Usage)

```sh
$ ./trans text/file/dir SRC [engine] [src_lang] [tgt_lang]
```

第一引数：翻訳対象種別（テキスト(text)、ファイル(file)、ディレクトリ(dir)のいずれか）を指定  
第二引数：翻訳対象（テキストなら文字列、ファイルならファイル名、ディレクトリならディレクトリ名）を指定  
第三引数：翻訳エンジン名（指定が無ければ"generalNT"）を指定  
第四引数：翻訳元言語名（指定が無ければ"ja"）を指定  
第五引数：翻訳先言語名（指定が無ければ"en"）を指定

1st argument : Specify the type to be translated ("text" or "file" or "dir")  
2nd argument : Specify the translation target (string for "text", file name for "file", directory name for "dir")  
3rd argument : Specify the translation engine name ("generalNT" if not specified)  
4th argument : Specify the source language name ("ja" if not specified)  
5th argument : Specify the target language name ("en" if not specified)


### 使用例(Examples)
```sh
$ ./trans text "吾輩は猫である。"
I am a cat.

$ echo -e "吾輩は猫である。\n名前はまだない。" | ./trans text
I am a cat.
No name yet.

$ ./trans text "吾輩は猫である。" generalNT ja de
Ich bin eine Katze.

$ echo -e "吾輩は猫である。\n名前はまだない。" | ./trans text "" generalNT ja de
Ich bin eine Katze.
Ich habe noch keinen Namen.
```

```sh
$ ./trans file sample.docx
translating "/path/to/file/sample.docx" to "/path/to/file/sample_en.docx", pid is XXXXX, state is 0.
 ...
translating "/path/to/file/sample.docx" to "/path/to/file/sample_en.docx", pid is XXXXX, state is 1.
 ...
translating "/path/to/file/sample.docx" to "/path/to/file/sample_en.docx", pid is XXXXX, state is 2.
translated results are written in /path/to/file/sample_en.docx.
```

```sh
$ ./trans dir sample_dir
start translating files from "/path/to/sample_dir" to "/path/to/sample_dir_en"
translating "/path/to/sample_dir/xxxxxxx" to "/path/to/sample_dir_en/xxxxxxx"
 ...
```


## 留意事項(Notice)

本プログラムから、「みんなの自動翻訳@TexTra」のサービスを利用する場合は、ユーザー登録の上、下記の利用規約を守って使ってください。  
みんなの自動翻訳@TexTra　利用規約　https://mt-auto-minhon-mlt.ucri.jgn-x.jp/content/policy/

When you use "みんなの自動翻訳@TexTra" through this program, you should first register your user name and password,   
then, you should observe its "Term of Use" (https://mt-auto-minhon-mlt.ucri.jgn-x.jp/content/policy/).

