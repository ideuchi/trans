while line = gets
  line.gsub!(/｟/,"")
  line.gsub!(/｠/,"")
  puts line
end
