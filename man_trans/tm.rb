TM = 
{"NAME", "名前",
"SYNOPSIS", "書式",
"DESCRIPTION", "説明",
"OPTION", "オプション",
"OPTIONS", "オプション",
"FILE", "ファイル",
"FILES", "ファイル",
"SEE ALSO", "関連項目",
"BUG", "バグ",
"BUGS", "バグ",
"AUTHOR", "作者",
"AUTHORS", "作者",
"ENVIRONMENT", "環境",
"ENVIRONMENT VARIABLES", "環境変数",
"EXAMPLES", "例",
"EXAMPLE", "例",
"REPORTING BUGS", "バグ報告",
"COPYRIGHT", "著作権",
"QUICK SUMMARY", "概要",
"SUMMARY", "概要",
"DIAGNOSTICS", "診断",
"RETURN VALUE", "戻り値",
}

while line = gets
  puts line
  if line =~ /^#\. type: SH/
    trans = nil
    while line = gets
      if line =~ /^msgid "(.+)"/
        header = $1
        trans = TM[header] if TM[header]
        puts line
      elsif line =~ /^msgstr ".+"/ && trans
        puts "msgstr \"#{trans}\""
      else
        puts line
      end
      break if line =~ /^\s$/
    end
  end
end
