while line = gets
  puts line
  if line =~ /msgid ""/
    eng = []
    allN = true
    while line = gets
      break if line =~ /msgstr/
      puts line
      eng.push(line.chomp)
      if line !~ /\\n"$/ && line !~ /^"\s+/
        allN = false
      end
    end
    if allN
      puts "msgstr \"\""
      puts eng
    else
      puts line
    end
  elsif line =~ /msgid "(.+\\n)"/
    org = $1
    line = gets
    if line =~ /msgstr ".+\\n"/
      puts "msgstr \"#{org}\""
    else
      puts line
    end
  end
end
