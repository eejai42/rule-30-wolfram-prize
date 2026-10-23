"""Third cycle: adversarial controls and falsification of proof shortcuts."""
from pathlib import Path
from itertools import product
import json
R=Path(__file__).parent;O=R/'data'
def z(k,t):return int(k==0 or (k>0 and t%(1<<k)==(k+1)//2)) if k>=0 else 0
violations=[]
for t in range(20):
 for k in range(1,41):
  expected=z(k,t)^(z(k-1,t)|z(k-2,t))
  if z(k,t+1)!=expected:violations.append({'k':k,'t':t,'actual_next':z(k,t+1),'rule30_next':expected})
assert [z(t,t) for t in range(20)]==[1,1]+[0]*18
assert all(z(k,t)==0 for t in range(20) for k in range(2*t+1,50))
# Exact period antiderivative lemma for ALL binary forcing words of lengths <=10.
count=0
for Q in range(1,11):
 for word in product((0,1),repeat=Q):
  least=next(p for p in range(1,Q+1) if Q%p==0 and all(word[t]==word[t%p] for t in range(Q)))
  if least!=Q:continue
  P=Q*(1+sum(word)%2);v=0;y=[]
  for t in range(2*P):y.append(v);v^=word[t%Q]
  actual=next(p for p in range(1,P+1) if all(y[t]==y[t+p] for t in range(P)))
  assert actual==P;count+=1
# Generic n-step truth table balances under variable initial states; this does
# not imply anything about temporal balance of the single fixed seed.
balance=[]
for n in range(1,7):
 ones=0;total=1<<(2*n+1)
 for w in range(total):
  row=[(w>>i)&1 for i in range(2*n+1)]
  for t in range(n):row=[row[i-1]^(row[i]|row[i+1]) for i in range(1,len(row)-1)]
  ones+=row[0]
 assert ones*2==total
 balance.append({'n':n,'assignments':total,'output_ones':ones})
# ACID serial order does not imply order independence.
add=lambda x:x+1;double=lambda x:2*x
assert double(add(0))!=add(double(0))
# Average is not a mergeable scalar without retaining weights.
a=[0];b=[10,10,10]
assert ((sum(a)/len(a))+(sum(b)/len(b)))/2!=sum(a+b)/len(a+b)
res={'diagonal_countermodel_center':[z(t,t) for t in range(20)],'first_rule30_violation':violations[0], 'forcing_words_exhaustively_verified':count,'generic_input_balance':balance,'acid_serial_orders':[double(add(0)),add(double(0))], 'average_of_averages':5,'pooled_average':7.5}
(O/'adversarial_results.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
