f = open("key.txt", "w+")
for i in range(21, 126):
    ch = chr(i)
    f.write(ch)
f.close()