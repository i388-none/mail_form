#!/usr/bin/ruby
# -*- coding: utf-8 -*-

print "Content-type: text/html\n\n"

require "cgi"
require "rubygems"
require "tmail"
require "net/smtp"
#require 'digest/md5'
#require 'cgi/session'

cgi = CGI.new

#session = CGI::Session.new(cgi)
#key = Digest::MD5.new.update('131072');

#メール設定
@mail_to      = "MAIL_TO"
@mail_from    = "MAIL_FROM"
@mail_subject = "お問い合わせ"
@form_url     = "http://*****.**/mail.cgi" 

#お問い合わせ項目設定
items = ["お問い合わせ1", "お問い合わせ2", "お問い合わせ3"]

#入力チェック
def send_check(cgi)

  error_str = ""
  if (cgi['email'] == '')
    error_str = 'メールアドレスを入力してください。<br>'
    email_empty_flg = 1
  end

  if (cgi['email_confirm'] == '')
    error_str =  error_str + 'メールアドレス確認を入力してください。<br>'
    email_empty_flg = 1
  end
  
  if (email_empty_flg != 1) 

    if (/^[a-zA-Z0-9!$&*.=^`|~#%'+\/?_{}-]+@([a-zA-Z0-9_-]+\.)+[a-zA-Z]{2,4}$/ =~ cgi['email'])
    else
      error_str = error_str + 'メールアドレスが正しくありません。<br>'
      mail_error_flg = 1
    end
  end

  if (mail_error_flg != 1)
    if (cgi['email'] != cgi['email_confirm'])
           error_str = error_str + 'メールアドレス確認が一致しません。<br>'
    end
  end
  
  if (cgi['remarks'] == '')
     error_str = error_str + 'お問い合わせ内容を入力してください。<br>'
  end

  return error_str

end

#メール送信処理
def mail_send(cgi)
  begin
    mail         = TMail::Mail.new
    mail.from    = @mail_from
    mail.subject = @mail_subject

    #本文
    mail_text = "【メールアドレス】\n"
    mail_text = mail_text + "#{cgi['email']}\n\n"
    mail_text = mail_text + "【お問い合わせ項目】\n"
    mail_text = mail_text + "#{cgi['item']}\n\n"
    mail_text = mail_text + "【お問い合わせ内容】\n"
    mail_text = mail_text + "#{cgi['remarks']}\n\n"
    mail_text = mail_text + "【IPアドレス】\n"
    mail_text = mail_text + "#{ENV['REMOTE_ADDR']}\n\n"

    mail.body         = NKF.nkf("-j", mail_text)
    mail.content_type = "text/plain"
    mail.charset      = "iso-2022-jp"

    smtp = Net::SMTP.new("localhost", 25)

    smtp.start do |s|
      s.send_mail(mail.encoded, mail.from, @mail_to)
    end
  rescue => evar
    print "mail send error"
    exit
  end
end


#POST時
case  cgi["view_flg"]

when "1"
  error_str = send_check(cgi)
  if (error_str != "") 
    view_flg = 1
  else
    post_email   = CGI.escapeHTML(cgi['email'])
    post_item    = CGI.escapeHTML(cgi['item'])
    post_remarks = CGI.escapeHTML(cgi['remarks'])

    view_flg = 2
  end
when "2"
  if @form_url == ENV["HTTP_REFERER"] then
    mail_send(cgi)
  end
  
  view_flg = 3
else
  view_flg = 1
end

html_head = <<EOM
<html>
<head>
<meta http-equiv="Content-type" content="text/html; charset=utf-8">
<title> お問い合わせ </title>
</head>
<body>
<div align="center">-- お問い合わせ --</div><br>
<div style="font-size:12px;color:#ff0000">#{error_str}</div>
EOM

#お問い合わせ項目のセット
item_option = ""
items.each do |item|
  option_tag = "<option>#{item}</option>"
  item_option = item_option + option_tag
end

html_form = <<EOM
<form action="mail.cgi" method="post">
<input type="hidden" name="view_flg" value="1">

<label style="font-size:10px;font-weight:bold">メールアドレス:</label><br>
<input type="text" name="email" value="" size="40" MODE="alphabet"><br><br>

<label style="font-size:10px;font-weight:bold">メールアドレス確認:</label><br>
<input type="text" name="email_confirm" value="" size="40" MODE="alphabet"><br><br>

<label style="font-size:10px;font-weight:bold">お問い合わせ項目:</label><br>
<select name="item">
#{item_option}
</select><br><br>

<label style="font-size:10px;font-weight:bold">お問い合わせ内容:</label><br>
<textarea name="remarks" cols="25" rows="10"></textarea><br>

<div align="center"><input type="submit" value="確認"></div>
</form>
EOM

html_confirm = <<EOM
<p style="font-size:12px">以下のお問い合わせ内容をご確認の上、送信ボタンを押してください</p>
<form action="mail.cgi" method="post">
<input type="hidden" name="view_flg" value="2">
<input type="hidden" name="email" value="#{post_email}">
<input type="hidden" name="item" value="#{post_item}">
<input type="hidden" name="remarks" value="#{post_remarks}">

<label style="font-size:10px;font-weight:bold">【メールアドレス】</label>
<p>#{post_email}</p>

<label style="font-size:10px;font-weight:bold">【お問い合わせ項目】</label>
<p>#{post_item}</p>

<label style="font-size:10px;font-weight:bold">【お問い合わせ内容】</label>
<p>#{post_remarks}</p>

<div align="center"><input type="submit" value="送信"></div>
</form>
EOM

html_complate = <<EOM
<p style="font-size:12px">送信完了しました。</p>
<div align="center"><a href="mail.cgi">戻る</a></div>
EOM


html_footer = <<EOM
</body>
</html>
EOM

print html_head

case view_flg
when 1
  print html_form
when 2
  print html_confirm
when 3
  print html_complate
end

print html_footer
