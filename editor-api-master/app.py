import re

import paddle
import paddlenlp
from flask import Flask, request, jsonify
from flask_cors import CORS
from paddlenlp.transformers import UNIMOLMHeadModel

from generation.utils import post_process_sum
from correction.corrector import Corrector

app = Flask(__name__)
CORS(app, supports_credentials=True)

# 设置模型名称
MODEL_NAME = 'unimo-text-1.0'
tokenizer = paddlenlp.transformers.UNIMOTokenizer.from_pretrained(MODEL_NAME)
layer_state_dict = paddle.load("generation/textgen.pdparams")
model = UNIMOLMHeadModel.from_pretrained(MODEL_NAME)
model.set_state_dict(layer_state_dict)

num_return_sequences = 8  #


@app.route('/textGen', methods=['post'])
def textGen():
    inputs = request.get_json()['content']
    inputs_ids = tokenizer.gen_encode(
        inputs,
        return_tensors=True,
        add_start_token_for_decoding=True,
        return_position_ids=True)

    # 调用生成api并指定解码策略为beam_search
    outputs, scores = model.generate(**inputs_ids, decode_strategy='beam_search', num_beams=8,
                                     num_return_sequences=num_return_sequences)
    text = ''.join(post_process_sum(outputs[0].numpy(), tokenizer)[1])
    return jsonify({'status': '200', 'text': text})


@app.route('/textCorrect', methods=['post'])
def textCorrect():
    inputs = request.get_json()['content']
    inputs = re.split('[ ，。\n]', inputs)
    print(inputs)

    outputs = []
    ct = Corrector()
    cnt = 0
    for line in inputs:
        correct_sent, err = ct.correct(line)
        if err:
            cnt += 1
            if len(outputs) == 0:
                outputs.append("{}.\n{}\n=>\n{}\n{}".format(cnt, line, correct_sent, err))
            else:
                outputs.append("\n\n{}.\n{}\n=>\n{}\n{}".format(cnt, line, correct_sent, err))
    print(outputs)

    return jsonify({'status': '200', 'resultList': outputs})


if __name__ == '__main__':
    app.run(debug=True)
