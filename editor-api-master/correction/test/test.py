import pandas as pd

from correction.corrector import Corrector

ct = Corrector()
test_data = pd.read_csv('test.txt', delim_whitespace=True, names=["sent", "correct"])
ans = 0
for i in range(len(test_data)):
    sent = test_data.iloc[i]['sent']
    correct = test_data.iloc[i]['correct']
    correct_sent, err = ct.correct(sent)
    if correct_sent == correct:
        ans += 1
    print("ori_sent:{} =>\ncorrect_sent:{}\nresult:{}".format(sent, correct, correct_sent))
print(ans * 1.0 / len(test_data))
