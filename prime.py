n=8
for i in range(1,n):
    if n%i==0:
        k=1
    else:
        k=0
if k==1:
    print("not prime")
elif k==0:
    print("not")
    
