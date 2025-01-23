import re

x = input()
#print("word inputted:" + x)

x_manu = ''.join(x.split())

print("word maipulated:" + x_manu)

# Set a variable to temporarily store statements
string_array_tmp = re.findall("[^。]+。?", x)
string_array = []

#print(string_array_tmp)

for s in string_array_tmp:
    if len(s) > 70:
        for cs in s.split('、'):
            string_array.append(cs + '\r\n')
    else:
        string_array.append(s + '\r\n')

print(string_array)

f = open("F:\zundamon\devide.txt","w")
f.writelines(string_array)
f.close