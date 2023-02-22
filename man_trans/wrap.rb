while line = gets
  line.gsub!(/([BIE]<\s*[^\s]+\s*>)/){|x|
    "｟#{x}｠"
  }
  puts line
end
