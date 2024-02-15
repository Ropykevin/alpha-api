N = int(input())
list = []
for i in range(1, N):
    num = input().split()
    if num[0] == "insert":
        list.insert(int(num[1]), int(num[2]))
    elif num[0] == "print":
        print(list)
    elif num[0] == "remove":
        list.remove(int(num[1]))
    elif num[0] == "append":
        list.append(int(num[1]))
    elif num[0] == "sort":
        list.sort()
    elif num[0] == "pop":
        list.pop()
    elif num[0] == "reverse":
        list.reverse()

print(list)
