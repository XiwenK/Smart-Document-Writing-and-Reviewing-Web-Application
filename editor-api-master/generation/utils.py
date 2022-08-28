import paddle
from paddlenlp.data import Pad
import numpy as np
from paddlenlp.metrics import BLEU
from paddlenlp.transformers import BasicTokenizer


def calc_bleu(preds, targets):
    assert len(preds) == len(targets), (
        'The length of pred_responses should be equal to the length of '
        'target_responses. But received {} and {}.'.format(
            len(preds), len(targets)))
    bleu4 = BLEU(n_size=4)
    tokenizer = BasicTokenizer()

    for pred, target in zip(preds, targets):
        pred_tokens = tokenizer.tokenize(pred)
        target_token = tokenizer.tokenize(target)

        bleu4.add_inst(pred_tokens, [target_token])

    print('\n' + '*' * 15)
    print('The auto evaluation result is:')
    print('BLEU-4:', bleu4.score())


def convert_example(example, tokenizer, mode='train'):
    """convert an example into necessary features"""
    if mode != 'test':
        tokenized_example = tokenizer.gen_encode(
            example['first'],
            target=example['second'],
            return_position_ids=True,
            return_length=True)
        target_start = tokenized_example['input_ids'].index(
            tokenizer.cls_token_id, 1)
        target_end = tokenized_example['seq_len']
        tokenized_example['masked_positions'] = list(
            range(target_start, target_end - 1))
        tokenized_example['labels'] = tokenized_example['input_ids'][
                                      target_start + 1:target_end]
    else:
        tokenized_example = tokenizer.gen_encode(
            example['first'],
            add_start_token_for_decoding=True,
            return_position_ids=True)
        if 'second' in example and example['second']:
            tokenized_example['target'] = example['second']
    return tokenized_example


def batchify_fn(batch_examples, pad_val, mode):
    def pad_mask(batch_attention_mask):
        batch_size = len(batch_attention_mask)
        max_len = max(map(len, batch_attention_mask))
        attention_mask = np.ones(
            (batch_size, max_len, max_len), dtype='float32') * -1e9
        for i, mask_data in enumerate(attention_mask):
            seq_len = len(batch_attention_mask[i])
            mask_data[-seq_len:, -seq_len:] = np.array(
                batch_attention_mask[i], dtype='float32')
        # In order to ensure the correct broadcasting mechanism, expand one 
        # dimension to the second dimension (n_head of Transformer).
        attention_mask = np.expand_dims(attention_mask, axis=1)
        return attention_mask

    pad_func = Pad(pad_val=pad_val, pad_right=False, dtype='int64')

    input_ids = pad_func([example['input_ids'] for example in batch_examples])
    token_type_ids = pad_func(
        [example['token_type_ids'] for example in batch_examples])
    position_ids = pad_func(
        [example['position_ids'] for example in batch_examples])

    attention_mask = pad_mask(
        [example['attention_mask'] for example in batch_examples])

    if mode != 'test':
        max_len = max([example['seq_len'] for example in batch_examples])
        masked_positions = np.concatenate([
            np.array(example['masked_positions']) +
            (max_len - example['seq_len']) + i * max_len
            for i, example in enumerate(batch_examples)
        ])
        labels = np.concatenate([
            np.array(
                example['labels'], dtype='int64') for example in batch_examples
        ])
        return input_ids, token_type_ids, position_ids, attention_mask, masked_positions, labels
    else:
        return input_ids, token_type_ids, position_ids, attention_mask


@paddle.no_grad()
def evaluation(model, data_loader, tokenizer, num_beams):
    print('\nEval begin...')
    model.eval()
    pred_ref = []
    for step, inputs in enumerate(data_loader, 1):
        input_ids, token_type_ids, position_ids, attention_mask = inputs
        ids, scores = model.generate(
            input_ids=input_ids,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            attention_mask=attention_mask,
            decode_strategy='beam_search',
            num_beams=num_beams,
            bos_token_id=tokenizer.cls_token_id,
            eos_token_id=tokenizer.mask_token_id)

        results = select_sum(ids, scores, tokenizer, 20, 1)
        pred_ref.extend(results)

    with open('predictions.txt', 'w', encoding='utf-8') as fout:
        for ref in pred_ref:
            fout.write(ref + '\n')

    print('\nSave inference result into: predictions.txt')

    if 'target' in data_loader.dataset[0].keys():
        targets = [example['target'] for example in data_loader.dataset]
        calc_bleu(pred_ref, targets)

    model.train()
    return


def post_process_sum(token_ids, tokenizer):
    """Post-process the decoded sequence. Truncate from the first <eos>."""
    eos_pos = len(token_ids)
    for i, tok_id in enumerate(token_ids):
        if tok_id == tokenizer.mask_token_id:
            eos_pos = i
            break
    token_ids = token_ids[:eos_pos]
    tokens = tokenizer.convert_ids_to_tokens(token_ids)
    tokens = tokenizer.merge_subword(tokens)
    special_tokens = ['[UNK]']
    tokens = [token for token in tokens if token not in special_tokens]
    return token_ids, tokens


def select_sum(ids, scores, tokenizer, max_dec_len=None,
               num_return_sequences=1):
    results = []
    group = []
    tmp = []
    if scores is not None:
        ids = ids.numpy()
        scores = scores.numpy()

        if len(ids) != len(scores) or (len(ids) % num_return_sequences) != 0:
            raise ValueError(
                "the length of `ids` is {}, but the `num_return_sequences` is {}".
                    format(len(ids), num_return_sequences))

        for pred, score in zip(ids, scores):
            pred_token_ids, pred_tokens = post_process_sum(pred, tokenizer)
            num_token = len(pred_token_ids)

            target = "".join(pred_tokens)

            # not ending
            if max_dec_len is not None and num_token >= max_dec_len:
                score -= 1e3

            tmp.append([target, score])
            if len(tmp) == num_return_sequences:
                group.append(tmp)
                tmp = []

        for preds in group:
            preds = sorted(preds, key=lambda x: -x[1])
            results.append(preds[0][0])
    else:
        ids = ids.numpy()

        for pred in ids:
            pred_token_ids, pred_tokens = post_process_sum(pred, tokenizer)
            num_token = len(pred_token_ids)
            response = "".join(pred_tokens)

            # TODO: Support return scores in FT.
            tmp.append([response])
            if len(tmp) == num_return_sequences:
                group.append(tmp)
                tmp = []

        for preds in group:
            results.append(preds[0][0])

    return results
