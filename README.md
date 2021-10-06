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


## 応用例：Slackメッセージの翻訳／arXivから論文情報取得し投稿、返信に翻訳結果を追加

### Slackメッセージの翻訳

以下の手順で、翻訳支援コマンドツール(trans)を利用してSlackに投稿されたメッセージを翻訳するSlackアプリを作成できます。  
Slackアプリ作成に必要なファイルも本リポジトリに入れてあります。  

1. 連携先のSlackワークスペースにログインします。  
ログイン後、 https://api.slack.com/apps にアクセスして、"Create New App"をクリックします。  
"From scratch / From an app manifest"と表示された場合は、"From scratch"を選択します。  
出てくる画面に、Slackアプリの名前を入力し、デプロイ先のSlackワークスペースを選択します。  

2. 1.の後に表示されるアプリの設定画面で、"Add features and functionality"をの設定項目から、"Permissions"をクリックします。  
"Scopes"の"Bot Token Scopes"に、以下を一つずつ追加していきます。  
（一度、画面を閉じてしまった場合は、 https://api.slack.com/apps にアクセスして、1.で作成したSlackアプリ名をクリックすると設定画面が開きます。）  
- reactions:read
- chat:write:public（これを追加すると、同時にchat:writeも追加されます）
- channels:read
- channels:history
- groups:history
- im:history
- mpim:history

3. Slackアプリの設定画面の左側メニュー"Settings"カテゴリにある"Install App"をクリックします。  
表示された画面で、"Install to Workspace"をクリックすると、ワークスペースの画面に遷移し1.で作成したSlackアプリが連携先のSlackワークスペースにアクセスする権限をリクエストしている旨を伝える画面が開きます。  
「許可する」をクリックします。  

4. 3.を終えると、Slackアプリの設定画面に戻り、"OAuth Tokens for Your Workspace"の画面が表示されます。  
この画面で、"Bot User OAuth Token"として表示された"xoxb-12345..."といった文字列を控えておきます。  
（ここで"Bot User OAuth Token"で表示された文字列を控え忘れた場合は、Slackアプリ設定画面の左側メニュー"Features"カテゴリにある"OAuth & Permissions"から参照できます。）  

5. Slackアプリの設定画面の左側メニュー"Settings"カテゴリにある"Basic Information"をクリックします。  
"App Credentials"の"Verification Token"に表示された値を控えておきます。  
また、"Display Information"からSlackアプリのアイコンを設定できるので、textra-icon-512x512.pngを指定します。
（ここまでの手順で、2.で指定した権限を持ち、Slackワークスペースを操作できるSlackアプリが作成できました。実際の操作はSlack APIを経由して、6.でデプロイするHerokuアプリから行います。）

6. 本レポジトリの内容を、Herokuにデプロイします。  
Herokuのアプリ名は、後で必要になるので、控えておきます。  
以下のボタンを押して、必要事項を入力すればデプロイできます。

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/ideuchi/trans)  

gitコマンドとherokuコマンドを使う場合は、以下のようにコマンドを実行します。  
```sh
git clone https://github.com/ideuchi/trans
cd trans
heroku login   # login from browser
heroku create  # heroku app name is displayed by this command, https://[heroku_app_name].herokuapp.com/
git push heroku main

# replace string of [] by your own
heroku config:set NAME=[TexTra_user_name]
heroku config:set KEY=[TexTra_key]
heroku config:set SECRET=[TexTra_secret]
heroku config:set SLACK_BOT_TOKEN=[Slack_Bot_User_OAuth_Token in 4.]
heroku config:set SLACK_VERIFICATION_TOKEN=[Slack_Verification_Token in 5.]
```
（ここまでの手順で、Slackワークスペースを操作するHerokuアプリが準備できました。最後に、操作のきっかけとなるSlackのイベントをHerokuアプリに通知する設定が必要です。）

7. 連携先のSlackワークスペースにログインします。  
https://api.slack.com/apps にアクセスして、Slackアプリの設定画面を開き、"Add features and functionality"から、"Event Subscriptions"をクリックします。  
"Enable Events"をOnにして"Request URL"にHerokuアプリのURL https://[heroku-app-name].herokuapp.com/slack_events/ を入力します。  

8. "Enable Events"をOnにすると出てくる"Subscribe to bot events"に、"reaction_added"を追加します。  
画面下部の"Save Changes"をクリックすれば、設定が反映され、指定したイベントがHerokuアプリに通知されるようになります。  

9. 連携先のSlackワークスペースの画面左側の"App"に、1.で指定した名前のSlackアプリが表示されていることを確認してから、Slackアプリ名をクリックします。  
開いた画面の左上のSlackアプリ名をクリックすると出てくる画面で、"チャンネルにこのアプリを追加する"というボタンをクリックします。  
チャンネルを選んで、Slackアプリ（のボットユーザー）を追加します。  
Slackアプリ（のボットユーザー）を追加したチャンネルに、Slackアプリ（のボットユーザー）が追加された旨のメッセージが表示されていれば追加成功です。  

10. 【動作確認】Slackアプリ（のボットユーザー）を追加したチャンネルにメッセージを投稿し、そのメッセージに国旗アイコンのリアクションを追加します。  
メッセージの返信（スレッド）に、Slackアプリ（のボットユーザー）から翻訳結果が書き込まれれば正常動作しています。  
Herokuのdynoが生存している間は翻訳言語方向とメッセージ内容が重複した投稿を抑止する機能を追加したため、同じメッセージを何度も翻訳しても結果は返りません。

11. 正常動作していない場合など、翻訳アプリのログを確認したい場合は、ブラウザからHerokuアプリのURL https://[heroku-app-name].herokuapp.com/debug_cat/ にアクセスしてください。  
テキスト形式のログが参照できます。  
Herokuのdynoは最終リクエストから30分程度で、消えてしまいます。その際にログも消えてしまうので注意してください。  

ログを確認する場合、処理の流れは以下のようになっています。  

~~~~
処理のログ例（"Hello."を"こんにちは。"に翻訳する例）：
a. "starting handle reaction_added event."（reaction_addedイベントを受信した旨を記録）  
b. "emoji is one of target lang: emoji = jp, lang = ja"（絵文字の種類から翻訳処理対象かどうかを判定、この例では日本語への翻訳）  
c. "new event to handle: Ev027BNB2U4V"（Slackから複数回イベントが通知されることがあるため、新規イベントか処理中のイベントかを判定）  
d. "src message: Hello."（翻訳対象文字列を記録）  
e. "lang_detect cmd: ./trans lang_detect "Hello.""（言語判定コマンドの実行を記録）  
f. "lang_detect src_lang: it"（翻訳対象文字列の言語判定結果を記録、この例ではイタリア語、短い表現だとたまに間違える）  
g. "call get_trans_pairs(it, ja)"（翻訳対象文字列から、指定された言語への翻訳パス確認を行った旨を記録、この例ではイタリア語から日本語）  
h. "get_trans_pairs() result: ['it_en', 'en_ja']"（翻訳パスの結果を記録、この例ではイタリア語→英語、英語→日本語）
i. "response to reaction_added event:  
    cmd: ./trans text "Hello." generalNT it en | ./trans text "" generalNT en ja  
    res: こんにちは。"（呼び出した翻訳支援コマンドと、翻訳結果を記録。）
~~~~


### arXivから論文情報取得し投稿、返信に翻訳結果を追加

URL(https://[heroku-app-name].herokuapp.com/arxiv_check/)にアクセスすることで、arXivから論文情報を取得してくれる機能です（一日に一度を想定）。  
URLへのアクセスは、他の
指定した言語への翻訳結果を返信メッセージとして投稿してくれます。

1. Slackアプリの設定は「Slackメッセージの翻訳」の1～5と共通です。

2. デプロイ時のパラメタは以下のとおりです。
~~~~
ARXIV_CHECK_CHANNEL                 ：arXivから取得した論文情報の投稿先（チャンネルID）
ARXIV_CHECK_KEYWORD                 ：arXivから取得する論文の検索キーワード
ARXIV_CHECK_FROM_DAYS_BEFORE        ：何日前以降の論文を検索対象にするか（デフォルト値は'7'）
ARXIV_CHECK_TO_DAYS_BEFORE          ：何日前以前の論文を検索対象にするか（デフォルト値は'6'）
ARXIV_CHECK_AVOID_DUPLICATED_POSTING：短時間での重複投稿を避けるためのフラグ（デフォルト値は'ON'、Herokuのdynoが生存している間は重複投稿しなくなります）
ARXIV_CHECK_TRANS                   ：翻訳先言語
~~~~

3. デプロイ時のパラメタはURLパラメタで上書きできます。指定しなかったパラメタは、デプロイ時のパラメタが使われます。複数チャンネルへの投稿、複数キーワードでの検索を行いたい場合は、こちらを活用と便利です。
~~~~
post_channel            ：arXivから取得した論文情報の投稿先（チャンネルID）
keyword                 ：arXivから取得する論文の検索キーワード
dt_from                 ：何日前以降の論文を検索対象にするか
dt_to                   ：何日前以前の論文を検索対象にするか
avoid_duplicated_posting：短時間での重複投稿を避けるためのフラグ
trans_tgt_lang          ：翻訳先言語

https://[heroku-app-name].herokuapp.com/arxiv_check/?post_channel=Cxxxxxxxx&keyword=deep learning&trans_tgt_lang=ja
のように指定
~~~~



### Slackアプリ作成時の参考にさせていただいたサイト・プログラム：  
- reacjilator (Copyright (c) 2019 Tomomi Imura)  
https://github.com/slackapi/reacjilator
- django-slack-events-api (Copyright (c) 2017-present j-devel)  
https://github.com/j-devel/django-slack-events-api
- API by Django REST Framework  
https://qiita.com/kimihiro_n/items/86e0a9e619720e57ecd8
- About Python django  
https://www.sejuku.net/blog/9014


## 留意事項(Notice)

本プログラムから、「みんなの自動翻訳@TexTra」のサービスを利用する場合は、ユーザー登録の上、下記の利用規約を守って使ってください。  
みんなの自動翻訳@TexTra　利用規約　https://mt-auto-minhon-mlt.ucri.jgn-x.jp/content/policy/

When you use "みんなの自動翻訳@TexTra" through this program, you should first register your user name and password,   
then, you should observe its "Term of Use" (https://mt-auto-minhon-mlt.ucri.jgn-x.jp/content/policy/).

