while line = gets
  if line =~ /^msgid/
    puts line
    if line =~ /\\n/
      hasN = true
    else
      hasN = false
    end
    while line = gets
      if line =~ /^msgstr/
        if hasN
          line.gsub!(/"$/,'\n"')
        end
        puts line
        hasN = false
        break
      elsif line =~ /\\n/
        hasN = true
        puts line
      else
        puts line
      end
    end
  else
    puts line
  end
end
