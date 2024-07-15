import re
pattern = r"hello"
string = "hello world"
match_obj = re.match(pattern, string)
if match_obj:
    print("Match found:", match_obj.group())
else:
    print("No match")
